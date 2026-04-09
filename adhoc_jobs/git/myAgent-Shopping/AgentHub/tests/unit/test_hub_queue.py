import pytest
from datetime import datetime, timedelta
from agora.protocol.message import Message
from hub.msg_queue import MessageQueueManager, QueuedMessage


class TestMessageQueueManager:
    def test_enqueue_message(self):
        mgr = MessageQueueManager(ttl_seconds=300)
        msg = Message(
            msg_id="test-1",
            from_agent="a",
            to_agent="b",
            capability="test",
            payload={}
        )

        mgr.enqueue("agent_b", msg)
        assert mgr.queue_size("agent_b") == 1

    def test_dequeue_message(self):
        mgr = MessageQueueManager(ttl_seconds=300)
        msg = Message(
            msg_id="test-1",
            from_agent="a",
            to_agent="b",
            capability="test",
            payload={"key": "value"}
        )

        mgr.enqueue("agent_b", msg)
        queued = mgr.dequeue("agent_b")

        assert queued is not None
        assert queued.msg_id == "test-1"
        assert mgr.queue_size("agent_b") == 0

    def test_dequeue_empty(self):
        mgr = MessageQueueManager(ttl_seconds=300)
        queued = mgr.dequeue("nonexistent")
        assert queued is None

    def test_cleanup_expired(self):
        mgr = MessageQueueManager(ttl_seconds=1)
        msg = Message(
            msg_id="test-1",
            from_agent="a",
            to_agent="b",
            capability="test",
            payload={}
        )

        mgr.enqueue("agent_b", msg)
        # Simulate time passing
        for qm in mgr._queues["agent_b"]:
            qm.timestamp = datetime.utcnow() - timedelta(seconds=2)

        mgr.cleanup_expired()
        assert mgr.queue_size("agent_b") == 0

    def test_clear_queue(self):
        mgr = MessageQueueManager(ttl_seconds=300)
        msg = Message(
            msg_id="test-1",
            from_agent="a",
            to_agent="b",
            capability="test",
            payload={}
        )

        mgr.enqueue("agent_b", msg)
        mgr.clear_queue("agent_b")
        assert mgr.queue_size("agent_b") == 0
