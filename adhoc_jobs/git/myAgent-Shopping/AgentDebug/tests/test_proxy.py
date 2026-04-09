"""
A2ADebugProxy 单元测试
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
from aiohttp import web

from a2a_debugger.proxy.debug_proxy import A2ADebugProxy
from a2a_debugger.models.message import A2AMessage


class TestA2ADebugProxy:
    """测试调试代理核心功能"""

    @pytest.fixture
    def proxy(self):
        """创建测试代理实例"""
        return A2ADebugProxy(
            target_host="http://localhost:8000",
            listen_port=18080,
        )

    @pytest.mark.asyncio
    async def test_initialization(self, proxy):
        """测试初始化"""
        assert proxy.target_host == "http://localhost:8000"
        assert proxy.listen_port == 18080
        assert proxy._started is False
        assert len(proxy._hooks) == 0

    @pytest.mark.asyncio
    async def test_detect_message_type_request(self, proxy):
        """测试请求类型检测"""
        # 标准 JSON-RPC 请求
        assert proxy._detect_message_type(
            {"jsonrpc": "2.0", "method": "test", "id": 1}, True
        ) == "request"

        # Notification (无 id)
        assert proxy._detect_message_type(
            {"jsonrpc": "2.0", "method": "notify"}, True
        ) == "notification"

    @pytest.mark.asyncio
    async def test_detect_message_type_response(self, proxy):
        """测试响应类型检测"""
        # 成功响应
        assert proxy._detect_message_type(
            {"jsonrpc": "2.0", "result": "ok"}, False
        ) == "response"

        # 错误响应
        assert proxy._detect_message_type(
            {"jsonrpc": "2.0", "error": {"code": -1}}, False
        ) == "response"

    @pytest.mark.asyncio
    async def test_add_remove_hook(self, proxy):
        """测试钩子管理"""
        async def test_hook(msg):
            pass

        proxy.add_hook(test_hook)
        assert len(proxy._hooks) == 1
        assert test_hook in proxy._hooks

        # 移除钩子
        assert proxy.remove_hook(test_hook) is True
        assert len(proxy._hooks) == 0

        # 移除不存在的钩子
        assert proxy.remove_hook(test_hook) is False

    @pytest.mark.asyncio
    async def test_hook_execution(self, proxy):
        """测试钩子执行"""
        hook_called = False
        received_msg = None

        async def test_hook(msg):
            nonlocal hook_called, received_msg
            hook_called = True
            received_msg = msg

        proxy.add_hook(test_hook)

        # 创建测试消息
        msg = A2AMessage(id="test-1", source="a", target="b")

        # 手动触发钩子
        proxy._trigger_hooks(msg)

        # 等待异步任务完成
        await asyncio.sleep(0.1)

        assert hook_called is True
        assert received_msg is not None
        assert received_msg.id == "test-1"

    @pytest.mark.asyncio
    async def test_hook_exception_handling(self, proxy):
        """测试钩子异常处理"""
        async def bad_hook(msg):
            raise ValueError("Test error")

        proxy.add_hook(bad_hook)

        # 不应抛出异常
        msg = A2AMessage()
        proxy._trigger_hooks(msg)
        await asyncio.sleep(0.1)  # 等待异步任务

    @pytest.mark.asyncio
    async def test_get_message_store(self, proxy):
        """测试获取消息存储"""
        store = proxy.get_message_store()
        assert store is not None

    @pytest.mark.asyncio
    async def test_double_start(self, proxy):
        """测试重复启动应抛出异常"""
        # Mock runner 和 site 避免实际启动服务器
        with patch.object(proxy, '_runner'):
            with patch.object(proxy, '_site'):
                proxy._session = AsyncMock()
                proxy._started = True

                with pytest.raises(RuntimeError):
                    await proxy.start()


class TestA2ADebugProxyIntegration:
    """集成测试 - 需要实际启动服务"""

    @pytest.mark.asyncio
    async def test_full_request_response_cycle(self):
        """测试完整的请求响应周期"""

        # 创建模拟目标服务器
        async def target_handler(request):
            body = await request.json()
            return web.json_response({
                "jsonrpc": "2.0",
                "result": {"data": "success"},
                "id": body.get("id")
            })

        target_app = web.Application()
        target_app.router.add_post("/rpc", target_handler)

        target_runner = web.AppRunner(target_app)
        await target_runner.setup()
        target_site = web.TCPSite(target_runner, "localhost", 18081)
        await target_site.start()

        try:
            # 创建代理
            proxy = A2ADebugProxy(
                target_host="http://localhost:18081",
                listen_port=18082,
            )

            await proxy.start()

            try:
                # 发送请求通过代理
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "http://localhost:18082/rpc",
                        json={"jsonrpc": "2.0", "method": "test", "id": 1},
                        headers={"X-Agent-ID": "test-agent"},
                    ) as resp:
                        assert resp.status == 200
                        result = await resp.json()
                        assert result["result"]["data"] == "success"

                # 验证消息被记录
                store = proxy.get_message_store()
                messages = store.get_all()
                assert len(messages) == 2  # 请求 + 响应

                # 验证请求
                request_msg = messages[0]
                assert request_msg.message_type == "request"
                assert request_msg.source == "test-agent"
                assert request_msg.payload["method"] == "test"

                # 验证响应
                response_msg = messages[1]
                assert response_msg.message_type == "response"
                assert response_msg.metadata["request_id"] == request_msg.id

            finally:
                await proxy.stop()

        finally:
            await target_site.stop()
            await target_runner.cleanup()

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """测试超时处理"""

        # 创建慢速目标服务器
        async def slow_handler(request):
            await asyncio.sleep(35)  # 超过代理超时时间
            return web.json_response({"result": "ok"})

        target_app = web.Application()
        target_app.router.add_post("/slow", slow_handler)

        target_runner = web.AppRunner(target_app)
        await target_runner.setup()
        target_site = web.TCPSite(target_runner, "localhost", 18083)
        await target_site.start()

        try:
            proxy = A2ADebugProxy(
                target_host="http://localhost:18083",
                listen_port=18084,
            )
            await proxy.start()

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "http://localhost:18084/slow",
                        json={"method": "slow"},
                    ) as resp:
                        # 应返回 504 超时
                        assert resp.status == 504

            finally:
                await proxy.stop()

        finally:
            await target_site.stop()
            await target_runner.cleanup()

    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """测试连接错误处理"""

        # 使用未启动的端口
        proxy = A2ADebugProxy(
            target_host="http://localhost:59999",  # 未使用的端口
            listen_port=18085,
        )
        await proxy.start()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:18085/test",
                    json={"method": "test"},
                ) as resp:
                    # 应返回 502 错误
                    assert resp.status == 502

        finally:
            await proxy.stop()
