import pytest
from datetime import datetime
from agora.protocol.message import Message
from agora.protocol.codec import MessageCodec


class TestMessageCodec:
    def test_encode_message(self):
        msg = Message(
            msg_id="550e8400-e29b-41d4-a716-446655440000",
            from_agent="agent_a",
            to_agent="agent_b",
            capability="math.add",
            payload={"a": 1, "b": 2},
            timestamp=datetime(2025, 4, 8, 10, 0, 0),
            ttl=300
        )
        encoded = MessageCodec.encode(msg)
        assert isinstance(encoded, bytes)
        assert b"550e8400" in encoded

    def test_decode_message(self):
        json_str = '''{
            "msg_id": "550e8400-e29b-41d4-a716-446655440000",
            "from": "agent_a",
            "to": "agent_b",
            "capability": "math.add",
            "payload": {"a": 1, "b": 2},
            "timestamp": "2025-04-08T10:00:00",
            "ttl": 300,
            "correlation_id": null
        }'''
        msg = MessageCodec.decode(json_str.encode())
        assert msg.msg_id == "550e8400-e29b-41d4-a716-446655440000"
        assert msg.from_agent == "agent_a"
        assert msg.capability == "math.add"
        assert msg.payload == {"a": 1, "b": 2}

    def test_roundtrip(self):
        original = Message(
            msg_id="test-id",
            from_agent="a",
            to_agent="b",
            capability="test",
            payload={"key": "value"}
        )
        encoded = MessageCodec.encode(original)
        decoded = MessageCodec.decode(encoded)
        assert decoded.msg_id == original.msg_id
        assert decoded.from_agent == original.from_agent
        assert decoded.payload == original.payload
