"""
测试场景

演示完整的工作流程：启动代理 + 发送测试消息 + 分析结果。
"""

import asyncio
import json
import sys
import os

# 添加项目到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import aiohttp
from aiohttp import web

from a2a_debugger.proxy import A2ADebugProxy
from a2a_debugger.analyzer import ConversationAnalyzer


async def create_test_server(port: int):
    """创建测试服务器"""
    async def handler(request):
        await asyncio.sleep(0.05)  # 模拟处理延迟
        body = await request.json()

        method = body.get("method")
        msg_id = body.get("id")

        if method == "slow":
            await asyncio.sleep(2)  # 模拟慢请求

        result = {
            "received_method": method,
            "timestamp": asyncio.get_event_loop().time(),
        }

        return web.json_response({
            "jsonrpc": "2.0",
            "result": result,
            "id": msg_id,
        })

    app = web.Application()
    app.router.add_post("/rpc", handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", port)
    await site.start()

    return runner


async def send_test_requests(proxy_port: int, count: int = 10):
    """发送测试请求"""
    async with aiohttp.ClientSession() as session:
        for i in range(count):
            method = "test" if i < 8 else "slow" if i == 8 else "error"

            payload = {
                "jsonrpc": "2.0",
                "method": method,
                "params": {"index": i, "data": f"test-{i}"},
                "id": i,
            }

            try:
                async with session.post(
                    f"http://localhost:{proxy_port}/rpc",
                    json=payload,
                    headers={"X-Agent-ID": f"test-client-{i % 3}"},
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    result = await resp.json()
                    print(f"  请求 {i}: {method} -> status={resp.status}")
            except Exception as e:
                print(f"  请求 {i}: {method} -> error={e}")

            await asyncio.sleep(0.1)


async def main():
    """运行测试场景"""
    print("=" * 60)
    print("A2A Debugger 测试场景")
    print("=" * 60)

    # 1. 启动测试服务器
    print("\n1. 启动测试服务器...")
    server_port = 18090
    server = await create_test_server(server_port)
    print(f"   ✓ 测试服务器运行在 http://localhost:{server_port}")

    try:
        # 2. 启动调试代理
        print("\n2. 启动调试代理...")
        proxy_port = 18091
        proxy = A2ADebugProxy(
            target_host=f"http://localhost:{server_port}",
            listen_port=proxy_port,
        )
        await proxy.start()
        print(f"   ✓ 代理运行在 http://localhost:{proxy_port}")

        # 3. 发送测试请求
        print("\n3. 发送测试请求...")
        await send_test_requests(proxy_port, count=10)

        # 4. 分析结果
        print("\n4. 分析结果...")
        messages = proxy.get_message_store().get_all()
        print(f"   共记录 {len(messages)} 条消息")

        # 使用 ConversationAnalyzer 分析
        analyzer = ConversationAnalyzer(messages)

        # 统计
        stats = proxy.get_message_store().get_stats()
        print(f"\n   统计信息:")
        print(f"     - 总消息数: {stats['total']}")
        print(f"     - 请求数: {stats['requests']}")
        print(f"     - 响应数: {stats['responses']}")
        print(f"     - 错误数: {stats['errors']}")
        print(f"     - 错误率: {stats['error_rate']:.1f}%")

        # 延迟分析
        latency_stats = analyzer.latency_analysis()
        if latency_stats:
            print(f"\n   延迟分析:")
            for agent, ls in latency_stats.items():
                print(f"     - {agent}: avg={ls.avg_ms:.1f}ms, max={ls.max_ms:.1f}ms")

        # 循环检测
        cycles = analyzer.detect_cycles()
        print(f"\n   循环依赖: {len(cycles)} 个")

        # 诊断报告
        report = analyzer.generate_diagnosis_report()
        print(f"\n   诊断报告:")
        print(f"     - {report.summary}")
        if report.issues:
            for issue in report.issues:
                print(f"     - [{issue['severity']}] {issue['category']}: {issue['description']}")

        # 5. 显示消息详情
        print("\n5. 消息详情:")
        for msg in messages[:5]:
            status = msg.metadata.get("status", 200)
            latency = msg.get_latency_ms()
            print(f"   {msg.message_type:12} {msg.source:15} -> {msg.target:15} "
                  f"status={status} latency={latency:.1f}ms" if latency else "")

        print("\n" + "=" * 60)
        print("测试完成!")
        print("=" * 60)

        # 停止代理
        await proxy.stop()

    finally:
        # 停止服务器
        await server.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
