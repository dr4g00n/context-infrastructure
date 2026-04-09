"""
CLI 入口

提供命令行工具启动调试代理和查看信息。
"""

import argparse
import asyncio
import logging
import sys

from a2a_debugger.proxy.debug_proxy import A2ADebugProxy


def setup_logging(verbose: bool = False):
    """配置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="A2A Protocol Debugger - 调试代理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  a2a-debug --target http://localhost:8000 --port 8080
  a2a-debug -t http://localhost:8000 -p 8080 -v
        """,
    )

    parser.add_argument(
        "-t", "--target",
        required=True,
        help="目标服务地址 (例如: http://localhost:8000)",
    )

    parser.add_argument(
        "-p", "--port",
        type=int,
        default=8080,
        help="代理监听端口 (默认: 8080)",
    )

    parser.add_argument(
        "-H", "--host",
        default="localhost",
        help="代理监听地址 (默认: localhost)",
    )

    parser.add_argument(
        "-m", "--max-messages",
        type=int,
        default=10000,
        help="最大消息存储数 (默认: 10000)",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="启用详细日志",
    )

    args = parser.parse_args()

    setup_logging(args.verbose)

    async def run():
        proxy = A2ADebugProxy(
            target_host=args.target,
            listen_port=args.port,
            listen_host=args.host,
            max_messages=args.max_messages,
        )

        # 添加告警钩子示例
        async def alert_hook(msg):
            status = msg.metadata.get("status", 200)
            if status >= 500:
                logging.warning(f"🚨 Server error {status} detected!")

        proxy.add_hook(alert_hook)

        await proxy.start()

        print(f"\n{'='*60}")
        print(f"A2A Debug Proxy 正在运行")
        print(f"{'='*60}")
        print(f"代理地址: http://{args.host}:{args.port}")
        print(f"目标地址: {args.target}")
        print(f"\n按 Ctrl+C 停止")
        print(f"{'='*60}\n")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n正在停止...")
            await proxy.stop()
            print("已停止")

    try:
        asyncio.run(run())
    except Exception as e:
        logging.error(f"运行时错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
