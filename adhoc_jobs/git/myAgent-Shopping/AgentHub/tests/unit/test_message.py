import pytest
from datetime import datetime
from agora.protocol.message import Message


class TestMessage:
    def test_message_creation(self):
        msg = Message(
            msg_id="550e8400-e29b-41d4-a716-446655440000",
            from_agent="agent_a",
            to_agent="agent_b",
            capability="math.add",
            payload={"a": 1, "b": 2},
            timestamp=datetime(2025, 4, 8, 10, 0, 0),
            ttl=300
        )
        assert msg.msg_id == "550e8400-e29b-41d4-a716-446655440000"
        assert msg.from_agent == "agent_a"
        assert msg.to_agent == "agent_b"
        assert msg.capability == "math.add"
        assert msg.payload == {"a": 1, "b": 2}
        assert msg.ttl == 300
        assert msg.correlation_id is None

    def test_message_validation_missing_required(self):
        with pytest.raises(TypeError):
            Message(from_agent="agent_a")

    def test_message_default_ttl(self):
        msg = Message(
            msg_id="test-id",
            from_agent="a",
            to_agent="b",
            capability="test",
            payload={}
        )
        assert msg.ttl == 300
