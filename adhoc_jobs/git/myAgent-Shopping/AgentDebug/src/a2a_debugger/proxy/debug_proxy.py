"""
A2A 调试代理

提供透明的 HTTP 代理服务，拦截并记录所有 A2A 通信。
"""

import asyncio
import json
import logging
from typing import Callable, Awaitable, Optional
from datetime import datetime

import aiohttp
from aiohttp import web, ClientSession

from a2a_debugger.models.message import A2AMessage, MessageStore, MessageType


logger = logging.getLogger(__name__)


HookType = Callable[[A2AMessage], Awaitable[None]]


class A2ADebugProxy:
    """
    A2A 调试代理 - 拦截并记录所有通信

    作为透明代理运行，将请求转发到目标服务并记录完整交互。

    Attributes:
        target_host: 目标服务地址 (如 http://localhost:8000)
        listen_port: 代理监听端口
        message_store: 消息存储管理器
    """

    def __init__(
        self,
        target_host: str,
        listen_port: int = 8080,
        listen_host: str = "localhost",
        max_messages: int = 10000,
    ):
        """
        初始化调试代理

        Args:
            target_host: 目标服务基础 URL
            listen_port: 代理监听端口
            listen_host: 代理监听地址
            max_messages: 最大消息存储数
        """
        self.target_host = target_host.rstrip("/")
        self.listen_port = listen_port
        self.listen_host = listen_host
        self.message_store = MessageStore(max_size=max_messages)
        self._hooks: list[HookType] = []
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.TCPSite] = None
        self._session: Optional[ClientSession] = None
        self._started = False

    async def start(self) -> None:
        """启动调试代理服务器"""
        if self._started:
            raise RuntimeError("Proxy already started")

        # 创建持久化的 aiohttp session
        self._session = aiohttp.ClientSession()

        app = web.Application()
        app.router.add_route("*", "/{path:.*}", self._handle_request)

        self._runner = web.AppRunner(app)
        await self._runner.setup()

        self._site = web.TCPSite(self._runner, self.listen_host, self.listen_port)
        await self._site.start()

        self._started = True
        logger.info(
            f"🔍 A2A Debug Proxy listening on http://{self.listen_host}:{self.listen_port} "
            f"-> {self.target_host}"
        )

    async def stop(self) -> None:
        """停止调试代理服务器"""
        if not self._started:
            return

        if self._site:
            await self._site.stop()
        if self._runner:
            await self._runner.cleanup()
        if self._session:
            await self._session.close()

        self._started = False
        logger.info("A2A Debug Proxy stopped")

    async def _handle_request(self, request: web.Request) -> web.Response:
        """处理传入请求"""
        start_time = datetime.now()
        request_body = await request.read()

        # 记录请求
        request_msg = await self._record_request(request, request_body)

        # 构建目标 URL
        target_url = f"{self.target_host}{request.path_qs}"

        # 转发请求头 (排除 host)
        headers = {
            k: v for k, v in request.headers.items()
            if k.lower() != "host" and k.lower() != "content-length"
        }

        try:
            # 转发到目标服务
            async with self._session.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=request_body,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                response_body = await resp.read()

                # 计算延迟
                latency_ms = (datetime.now() - start_time).total_seconds() * 1000

                # 记录响应
                await self._record_response(
                    request_msg.id, resp, response_body, latency_ms
                )

                # 返回响应
                response_headers = dict(resp.headers)
                # 移除可能导致问题的头
                response_headers.pop("content-encoding", None)
                response_headers.pop("transfer-encoding", None)
                response_headers.pop("content-length", None)

                return web.Response(
                    status=resp.status,
                    headers=response_headers,
                    body=response_body,
                )

        except asyncio.TimeoutError:
            logger.warning(f"Timeout forwarding request to {target_url}")
            return web.Response(
                status=504,
                body=json.dumps({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32000,
                        "message": "Gateway Timeout",
                    },
                    "id": None,
                }).encode(),
                content_type="application/json",
            )

        except aiohttp.ClientError as e:
            logger.error(f"Error forwarding request: {e}")
            return web.Response(
                status=502,
                body=json.dumps({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32001,
                        "message": f"Bad Gateway: {str(e)}",
                    },
                    "id": None,
                }).encode(),
                content_type="application/json",
            )

    async def _record_request(
        self, request: web.Request, body: bytes
    ) -> A2AMessage:
        """记录请求消息"""
        # 解析 JSON body
        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            payload = {"_raw": body.decode("utf-8", errors="ignore") if body else {}}

        # 确定消息类型
        message_type = self._detect_message_type(payload, is_request=True)

        msg = A2AMessage(
            source=request.headers.get("X-Agent-ID", "unknown"),
            target="proxy",
            protocol_version=payload.get("jsonrpc", "2.0"),
            message_type=message_type,
            payload=payload,
            headers=dict(request.headers),
            metadata={
                "path": request.path,
                "method": request.method,
                "query": request.query_string,
            },
        )

        # 存储消息
        self.message_store.add(msg)

        # 触发钩子 (异步不阻塞)
        self._trigger_hooks(msg)

        return msg

    async def _record_response(
        self,
        request_id: str,
        response: aiohttp.ClientResponse,
        body: bytes,
        latency_ms: float,
    ) -> None:
        """记录响应消息"""
        # 解析 JSON body
        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            payload = {"_raw": body.decode("utf-8", errors="ignore") if body else {}}

        # 确定消息类型
        message_type = self._detect_message_type(payload, is_request=False)

        msg = A2AMessage(
            source="proxy",
            target="original-requester",
            protocol_version=payload.get("jsonrpc", "2.0"),
            message_type=message_type,
            payload=payload,
            headers=dict(response.headers),
            metadata={
                "request_id": request_id,
                "status": response.status,
                "latency_ms": latency_ms,
            },
        )

        # 存储消息并关联请求
        self.message_store.add(msg)
        self.message_store.link_response(request_id, msg.id)

        # 触发钩子
        self._trigger_hooks(msg)

    def _detect_message_type(self, payload: dict, is_request: bool) -> str:
        """检测消息类型"""
        if not is_request:
            return MessageType.RESPONSE.value

        # 请求类型：如果有 method 是 request，否则可能是 notification
        if "method" in payload:
            # 有 id 是 request，无 id 是 notification
            return MessageType.REQUEST.value if "id" in payload else MessageType.NOTIFICATION.value

        return MessageType.REQUEST.value

    def _trigger_hooks(self, msg: A2AMessage) -> None:
        """触发所有注册的钩子"""
        for hook in self._hooks:
            # 创建任务但不等待，避免阻塞
            asyncio.create_task(self._run_hook(hook, msg))

    async def _run_hook(self, hook: HookType, msg: A2AMessage) -> None:
        """运行单个钩子并捕获异常"""
        try:
            await hook(msg)
        except Exception as e:
            logger.error(f"Hook error: {e}")

    def add_hook(self, hook: HookType) -> None:
        """
        添加消息处理钩子

        钩子函数接收 A2AMessage 对象，可用于实时分析、告警等。

        Args:
            hook: 异步函数，接收 A2AMessage 参数
        """
        self._hooks.append(hook)

    def remove_hook(self, hook: HookType) -> bool:
        """
        移除消息处理钩子

        Returns:
            是否成功移除
        """
        if hook in self._hooks:
            self._hooks.remove(hook)
            return True
        return False

    def get_message_store(self) -> MessageStore:
        """获取消息存储实例"""
        return self.message_store

    async def __aenter__(self) -> "A2ADebugProxy":
        """异步上下文管理器入口"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """异步上下文管理器出口"""
        await self.stop()
