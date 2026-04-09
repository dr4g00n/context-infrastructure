# A2A Protocol Debugger

A2A (Agent-to-Agent) 协议调试工具，支持消息拦截、协议分析、可视化调试和故障诊断。

## 功能特性

- **消息拦截与记录**: 透明代理捕获所有 A2A 通信
- **实时调试界面**: 基于 Streamlit 的可视化仪表盘
- **协议合规检查**: 自动验证 JSON-RPC 和 A2A 协议规范
- **时序分析**: 请求-响应延迟分析和循环依赖检测
- **可扩展钩子**: 支持自定义消息处理逻辑

## 快速开始

### 安装

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -e ".[dev]"
```

### 启动调试代理

```python
import asyncio
from a2a_debugger import A2ADebugProxy

async def main():
    proxy = A2ADebugProxy(
        target_host="http://localhost:8000",
        listen_port=8080
    )
    await proxy.start()
    
    # 保持运行
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
```

### 启动 Web UI

```bash
streamlit run src/a2a_debugger/web/dashboard.py
```

## 项目结构

```
a2a_debugger/
├── src/a2a_debugger/
│   ├── models/          # 数据模型
│   ├── proxy/           # 调试代理
│   ├── analyzer/        # 协议分析
│   └── web/             # 可视化界面
├── tests/               # 测试
└── examples/            # 示例
```

## 开发

```bash
# 运行测试
pytest

# 代码格式化
black src tests
ruff check src tests --fix

# 类型检查
mypy src
```

## License

MIT License
