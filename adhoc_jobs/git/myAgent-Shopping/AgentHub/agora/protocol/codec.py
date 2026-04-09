"""Message encoding and decoding."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from agora.protocol.message import Message


class MessageCodec:
    """JSON codec for Message objects."""

    @staticmethod
    def encode(msg: Message) -> bytes:
        """Encode Message to JSON bytes."""
        data = {
            "msg_id": msg.msg_id,
            "from": msg.from_agent,
            "to": msg.to_agent,
            "capability": msg.capability,
            "payload": msg.payload,
            "timestamp": msg.timestamp.isoformat(),
            "ttl": msg.ttl,
            "correlation_id": msg.correlation_id
        }
        return json.dumps(data, separators=(',', ':')).encode('utf-8')

    @staticmethod
    def decode(data: bytes) -> Message:
        """Decode JSON bytes to Message."""
        obj = json.loads(data.decode('utf-8'))
        return Message(
            msg_id=obj["msg_id"],
            from_agent=obj["from"],
            to_agent=obj["to"],
            capability=obj["capability"],
            payload=obj["payload"],
            timestamp=datetime.fromisoformat(obj["timestamp"]),
            ttl=obj["ttl"],
            correlation_id=obj.get("correlation_id")
        )
