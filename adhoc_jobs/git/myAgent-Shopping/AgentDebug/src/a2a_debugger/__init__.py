"""
A2A Protocol Debugger - Agent-to-Agent 协议调试工具

提供消息拦截、协议分析、可视化调试等功能。
"""

__version__ = "0.1.0"

# 延迟导入避免循环依赖
__all__ = [
    "A2AMessage",
    "MessageStore",
    "MessageType",
    "A2ADebugProxy",
    "A2AMessageValidator",
    "ValidationResult",
    "ConversationAnalyzer",
]
