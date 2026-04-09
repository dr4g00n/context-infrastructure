"""Message format definitions for Agora protocol."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Message:
    """A message exchanged between Agents.

    Attributes:
        msg_id: Unique message identifier (UUID)
        from_agent: Sender Agent ID
        to_agent: Target Agent ID (empty for broadcast)
        capability: Target capability identifier
        payload: Business payload (JSON-serializable dict)
        timestamp: ISO8601 format timestamp
        ttl: Time-to-live in seconds (default: 300)
        correlation_id: For request-response correlation (optional)
    """
    msg_id: str
    from_agent: str
    to_agent: str
    capability: str
    payload: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ttl: int = 300
    correlation_id: str | None = None

    def is_expired(self) -> bool:
        """Check if message has exceeded its TTL."""
        from datetime import timedelta
        return datetime.utcnow() > self.timestamp + timedelta(seconds=self.ttl)
