"""
简单 Agent 示例

演示如何使用 A2A Debug Proxy 调试 Agent 间通信。
"""

import asyncio
import json
from aiohttp import web


async def agent_handler(request):
    """模拟 Agent 处理请求"""
    try:
        body = await request.json()

        method = body.get("method", "")
        msg_id = body.get("id")

        # 模拟不同的处理逻辑
        if method == "hello":
            result = {"message": "Hello from Agent!"}
        elif method == "add":
            params = body.get("params", {})
            a = params.get("a", 0)
            b = params.get("b", 0)
            result = {"sum": a + b}
        elif method == "error":
            # 模拟错误
            return web.json_response({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": "Invalid Request",
                },
                "id": msg_id,
            }, status=400)
        else:
            return web.json_response({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                },
                "id": msg_id,
            }, status=404)

        return web.json_response({
            "jsonrpc": "2.0",
            "result": result,
            "id": msg_id,
        })

    except json.JSONDecodeError:
        return web.json_response({
            "jsonrpc": "2.0",
            "error": {
                "code": -32700,
                "message": "Parse error",
            },
            "id": None,
        }, status=400)


async def health_check(request):
    """健康检查端点"""
    return web.json_response({"status": "ok"})


def create_app():
    """创建应用"""
    app = web.Application()
    app.router.add_post("/rpc", agent_handler)
    app.router.add_get("/health", health_check)
    return app


async def main():
    """启动示例 Agent"""
    app = create_app()

    runner = web.AppRunner(app)
    await runner.setup()

    port = 8000
    site = web.TCPSite(runner, "localhost", port)
    await site.start()

    print(f"🚀 示例 Agent 运行在 http://localhost:{port}")
    print(f"   RPC 端点: POST /rpc")
    print(f"   健康检查: GET /health")
    print("\n按 Ctrl+C 停止\n")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止...")
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
