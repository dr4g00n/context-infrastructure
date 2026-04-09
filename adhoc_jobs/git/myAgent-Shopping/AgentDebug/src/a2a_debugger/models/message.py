"""
A2A 协议消息模型

定义 A2A (Agent-to-Agent) 协议的消息结构和存储机制。
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Optional
from enum import Enum
import uuid
import json


class MessageType(str, Enum):
    """消息类型枚举"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"


@dataclass
class A2AMessage:
    """
    A2A 协议消息结构

    支持 JSON-RPC 2.0 风格的 Agent 间通信消息格式。

    Attributes:
        id: 消息唯一标识符
        timestamp: 消息创建时间戳
        source: 消息来源 Agent ID
        target: 消息目标 Agent ID
        protocol_version: 协议版本
        message_type: 消息类型 (request/response/notification)
        payload: 消息负载 (JSON-RPC 格式的 body)
        headers: HTTP 头信息
        metadata: 元数据 (状态码、延迟等附加信息)
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    target: str = ""
    protocol_version: str = "1.0"
    message_type: str = "request"
    payload: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """初始化后验证"""
        if self.message_type not in [t.value for t in MessageType]:
            raise ValueError(f"Invalid message_type: {self.message_type}")

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "target": self.target,
            "protocol_version": self.protocol_version,
            "message_type": self.message_type,
            "payload": self.payload,
            "headers": self.headers,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """序列化为 JSON 字符串"""
        return json.dumps(self.to_dict(), default=str, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "A2AMessage":
        """从字典创建消息对象"""
        # 处理时间戳
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            timestamp=timestamp,
            source=data.get("source", ""),
            target=data.get("target", ""),
            protocol_version=data.get("protocol_version", "1.0"),
            message_type=data.get("message_type", "request"),
            payload=data.get("payload", {}),
            headers=data.get("headers", {}),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "A2AMessage":
        """从 JSON 字符串创建消息对象"""
        return cls.from_dict(json.loads(json_str))

    def is_request(self) -> bool:
        """检查是否为请求消息"""
        return self.message_type == MessageType.REQUEST.value

    def is_response(self) -> bool:
        """检查是否为响应消息"""
        return self.message_type == MessageType.RESPONSE.value

    def is_notification(self) -> bool:
        """检查是否为通知消息"""
        return self.message_type == MessageType.NOTIFICATION.value

    def get_jsonrpc_version(self) -> Optional[str]:
        """获取 JSON-RPC 版本"""
        return self.payload.get("jsonrpc")

    def get_method(self) -> Optional[str]:
        """获取请求方法名 (仅请求类型)"""
        return self.payload.get("method")

    def get_error_code(self) -> Optional[int]:
        """获取错误码 (仅响应类型且包含错误)"""
        error = self.payload.get("error")
        if isinstance(error, dict):
            return error.get("code")
        return None

    def get_latency_ms(self) -> Optional[float]:
        """获取延迟 (毫秒),从 metadata 中提取"""
        latency = self.metadata.get("latency_ms")
        if latency is not None:
            return float(latency)
        return None


class MessageStore:
    """
    消息存储管理器

    提供内存中的消息存储、检索和过滤功能。
    支持最大容量限制以防止内存溢出。

    Attributes:
        max_size: 最大存储消息数 (默认 10000)
    """

    def __init__(self, max_size: int = 10000):
        self._messages: list[A2AMessage] = []
        self._max_size = max_size
        self._index_by_id: dict[str, int] = {}  # id -> index
        self._request_response_map: dict[str, str] = {}  # request_id -> response_id

    def add(self, message: A2AMessage) -> None:
        """添加消息到存储"""
        self._messages.append(message)
        self._index_by_id[message.id] = len(self._messages) - 1

        # 维护最大容量
        if len(self._messages) > self._max_size:
            removed = self._messages.pop(0)
            del self._index_by_id[removed.id]
            # 重建索引
            self._rebuild_index()

    def link_response(self, request_id: str, response_id: str) -> None:
        """关联请求和响应"""
        self._request_response_map[request_id] = response_id

    def get_by_id(self, message_id: str) -> Optional[A2AMessage]:
        """通过 ID 获取消息"""
        index = self._index_by_id.get(message_id)
        if index is not None and 0 <= index < len(self._messages):
            return self._messages[index]
        return None

    def get_response_for(self, request_id: str) -> Optional[A2AMessage]:
        """获取请求对应的响应消息"""
        response_id = self._request_response_map.get(request_id)
        if response_id:
            return self.get_by_id(response_id)
        return None

    def get_all(self) -> list[A2AMessage]:
        """获取所有消息 (按时间顺序)"""
        return self._messages.copy()

    def get_recent(self, count: int = 100) -> list[A2AMessage]:
        """获取最近 N 条消息"""
        return self._messages[-count:] if count < len(self._messages) else self._messages.copy()

    def filter_by_source(self, source: str) -> list[A2AMessage]:
        """按来源过滤消息"""
        return [m for m in self._messages if m.source == source]

    def filter_by_target(self, target: str) -> list[A2AMessage]:
        """按目标过滤消息"""
        return [m for m in self._messages if m.target == target]

    def filter_by_type(self, message_type: str) -> list[A2AMessage]:
        """按类型过滤消息"""
        return [m for m in self._messages if m.message_type == message_type]

    def filter_by_time_range(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> list[A2AMessage]:
        """按时间范围过滤消息"""
        result = self._messages
        if start:
            result = [m for m in result if m.timestamp >= start]
        if end:
            result = [m for m in result if m.timestamp <= end]
        return result

    def clear(self) -> None:
        """清空所有消息"""
        self._messages.clear()
        self._index_by_id.clear()
        self._request_response_map.clear()

    def get_stats(self) -> dict[str, Any]:
        """获取存储统计信息"""
        total = len(self._messages)
        if total == 0:
            return {
                "total": 0,
                "requests": 0,
                "responses": 0,
                "notifications": 0,
                "errors": 0,
            }

        requests = sum(1 for m in self._messages if m.is_request())
        responses = sum(1 for m in self._messages if m.is_response())
        notifications = sum(1 for m in self._messages if m.is_notification())

        # 统计 HTTP 错误 (从 metadata 中的 status 判断)
        errors = sum(
            1 for m in self._messages
            if m.metadata.get("status", 200) >= 400
        )

        return {
            "total": total,
            "requests": requests,
            "responses": responses,
            "notifications": notifications,
            "errors": errors,
            "error_rate": errors / total * 100,
        }

    def _rebuild_index(self) -> None:
        """重建索引"""
        self._index_by_id = {
            msg.id: idx for idx, msg in enumerate(self._messages)
        }

    def __len__(self) -> int:
        """返回消息数量"""
        return len(self._messages)

    def __iter__(self):
        """迭代所有消息"""
        return iter(self._messages)
