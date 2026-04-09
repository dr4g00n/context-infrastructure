"""
A2AMessage 和 MessageStore 单元测试
"""

import pytest
from datetime import datetime
from a2a_debugger.models.message import A2AMessage, MessageStore, MessageType


class TestA2AMessage:
    """测试 A2AMessage 数据类"""

    def test_default_creation(self):
        """测试默认创建"""
        msg = A2AMessage()
        assert msg.id
        assert msg.timestamp
        assert msg.message_type == "request"
        assert msg.protocol_version == "1.0"
        assert msg.payload == {}
        assert msg.headers == {}
        assert msg.metadata == {}

    def test_custom_creation(self):
        """测试自定义创建"""
        msg = A2AMessage(
            id="test-id",
            source="agent-a",
            target="agent-b",
            message_type="response",
            payload={"jsonrpc": "2.0", "result": "ok"},
            headers={"Content-Type": "application/json"},
            metadata={"status": 200},
        )
        assert msg.id == "test-id"
        assert msg.source == "agent-a"
        assert msg.target == "agent-b"
        assert msg.message_type == "response"
        assert msg.payload["result"] == "ok"

    def test_invalid_message_type(self):
        """测试无效消息类型应抛出异常"""
        with pytest.raises(ValueError):
            A2AMessage(message_type="invalid")

    def test_to_dict(self):
        """测试转换为字典"""
        msg = A2AMessage(
            id="test-123",
            source="a",
            target="b",
            payload={"method": "test"},
        )
        data = msg.to_dict()
        assert data["id"] == "test-123"
        assert data["source"] == "a"
        assert data["target"] == "b"
        assert data["payload"]["method"] == "test"
        assert isinstance(data["timestamp"], str)

    def test_to_json(self):
        """测试 JSON 序列化"""
        msg = A2AMessage(source="a", target="b")
        json_str = msg.to_json()
        assert "a" in json_str
        assert "b" in json_str

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "id": "msg-1",
            "source": "agent-x",
            "target": "agent-y",
            "message_type": "request",
            "payload": {"jsonrpc": "2.0", "method": "hello"},
            "timestamp": "2024-01-15T10:30:00",
        }
        msg = A2AMessage.from_dict(data)
        assert msg.id == "msg-1"
        assert msg.source == "agent-x"
        assert msg.payload["method"] == "hello"
        assert msg.timestamp.year == 2024

    def test_from_json(self):
        """测试从 JSON 创建"""
        json_str = '{"id": "j1", "source": "s1", "target": "t1", "message_type": "notification"}'
        msg = A2AMessage.from_json(json_str)
        assert msg.id == "j1"
        assert msg.is_notification()

    def test_message_type_checks(self):
        """测试消息类型检查方法"""
        request = A2AMessage(message_type="request")
        response = A2AMessage(message_type="response")
        notification = A2AMessage(message_type="notification")

        assert request.is_request()
        assert not request.is_response()

        assert response.is_response()
        assert not response.is_request()

        assert notification.is_notification()
        assert not notification.is_request()

    def test_get_jsonrpc_version(self):
        """测试获取 JSON-RPC 版本"""
        msg = A2AMessage(payload={"jsonrpc": "2.0"})
        assert msg.get_jsonrpc_version() == "2.0"

        msg2 = A2AMessage(payload={})
        assert msg2.get_jsonrpc_version() is None

    def test_get_method(self):
        """测试获取方法名"""
        msg = A2AMessage(payload={"method": "tools/call"})
        assert msg.get_method() == "tools/call"

    def test_get_error_code(self):
        """测试获取错误码"""
        msg = A2AMessage(payload={"error": {"code": -32600, "message": "Invalid Request"}})
        assert msg.get_error_code() == -32600

        msg2 = A2AMessage(payload={"result": "ok"})
        assert msg2.get_error_code() is None

    def test_get_latency_ms(self):
        """测试获取延迟"""
        msg = A2AMessage(metadata={"latency_ms": 150.5})
        assert msg.get_latency_ms() == 150.5


class TestMessageStore:
    """测试 MessageStore 存储管理"""

    def test_add_and_get(self):
        """测试添加和获取"""
        store = MessageStore()
        msg = A2AMessage(id="m1", source="a")
        store.add(msg)

        retrieved = store.get_by_id("m1")
        assert retrieved is not None
        assert retrieved.id == "m1"

    def test_get_nonexistent(self):
        """测试获取不存在消息"""
        store = MessageStore()
        assert store.get_by_id("not-exist") is None

    def test_get_recent(self):
        """测试获取最近消息"""
        store = MessageStore()
        for i in range(5):
            store.add(A2AMessage(id=f"m{i}"))

        recent = store.get_recent(3)
        assert len(recent) == 3
        assert recent[-1].id == "m4"

    def test_max_size_limit(self):
        """测试容量限制"""
        store = MessageStore(max_size=3)
        for i in range(5):
            store.add(A2AMessage(id=f"m{i}"))

        assert len(store) == 3
        assert store.get_by_id("m0") is None  # 最早被移除
        assert store.get_by_id("m4") is not None

    def test_filter_by_source(self):
        """测试按来源过滤"""
        store = MessageStore()
        store.add(A2AMessage(source="agent-a"))
        store.add(A2AMessage(source="agent-b"))
        store.add(A2AMessage(source="agent-a"))

        filtered = store.filter_by_source("agent-a")
        assert len(filtered) == 2

    def test_filter_by_type(self):
        """测试按类型过滤"""
        store = MessageStore()
        store.add(A2AMessage(message_type="request"))
        store.add(A2AMessage(message_type="response"))
        store.add(A2AMessage(message_type="request"))

        requests = store.filter_by_type("request")
        assert len(requests) == 2

    def test_link_response(self):
        """测试请求响应关联"""
        store = MessageStore()
        request = A2AMessage(id="req-1", message_type="request")
        response = A2AMessage(id="resp-1", message_type="response")

        store.add(request)
        store.add(response)
        store.link_response("req-1", "resp-1")

        linked = store.get_response_for("req-1")
        assert linked is not None
        assert linked.id == "resp-1"

    def test_get_stats(self):
        """测试统计信息"""
        store = MessageStore()
        store.add(A2AMessage(message_type="request"))
        store.add(A2AMessage(message_type="response", metadata={"status": 200}))
        store.add(A2AMessage(message_type="response", metadata={"status": 500}))

        stats = store.get_stats()
        assert stats["total"] == 3
        assert stats["requests"] == 1
        assert stats["responses"] == 2
        assert stats["errors"] == 1
        assert stats["error_rate"] == pytest.approx(33.33, rel=0.01)

    def test_clear(self):
        """测试清空"""
        store = MessageStore()
        store.add(A2AMessage(id="m1"))
        store.clear()

        assert len(store) == 0
        assert store.get_by_id("m1") is None

    def test_iteration(self):
        """测试迭代"""
        store = MessageStore()
        store.add(A2AMessage(id="m1"))
        store.add(A2AMessage(id="m2"))

        ids = [m.id for m in store]
        assert "m1" in ids
        assert "m2" in ids
