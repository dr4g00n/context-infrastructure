"""Hub message queue management with TTL."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from agora.protocol.message import Message


@dataclass
class QueuedMessage:
    """A message in the queue with metadata."""
    msg_id: str
    from_agent: str
    to_agent: str
    capability: str
    payload: dict
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def from_message(cls, msg: Message) -> QueuedMessage:
        return cls(
            msg_id=msg.msg_id,
            from_agent=msg.from_agent,
            to_agent=msg.to_agent,
            capability=msg.capability,
            payload=msg.payload
        )


class MessageQueueManager:
    """Manages per-Agent message queues with TTL."""

    def __init__(self, ttl_seconds: float = 300, max_size: int = 1000) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._queues: dict[str, deque[QueuedMessage]] = {}

    def enqueue(self, agent_id: str, message: Message) -> bool:
        """Add message to agent's queue. Returns False if queue full."""
        if agent_id not in self._queues:
            self._queues[agent_id] = deque()

        if len(self._queues[agent_id]) >= self.max_size:
            return False

        queued = QueuedMessage.from_message(message)
        self._queues[agent_id].append(queued)
        return True

    def dequeue(self, agent_id: str) -> QueuedMessage | None:
        """Get next message for agent. Returns None if empty."""
        if agent_id not in self._queues:
            return None

        queue = self._queues[agent_id]
        while queue:
            msg = queue.popleft()
            # Check if expired
            age = (datetime.utcnow() - msg.timestamp).total_seconds()
            if age <= self.ttl_seconds:
                return msg

        return None

    def queue_size(self, agent_id: str) -> int:
        """Get current queue size for agent."""
        return len(self._queues.get(agent_id, []))

    def clear_queue(self, agent_id: str) -> None:
        """Clear all messages for an agent."""
        self._queues.pop(agent_id, None)

    def cleanup_expired(self) -> int:
        """Remove expired messages from all queues. Returns count removed."""
        removed = 0
        cutoff = datetime.utcnow() - timedelta(seconds=self.ttl_seconds)

        for agent_id, queue in self._queues.items():
            original_len = len(queue)
            # Filter out expired messages
            self._queues[agent_id] = deque(
                msg for msg in queue if msg.timestamp > cutoff
            )
            removed += original_len - len(self._queues[agent_id])

        return removed
