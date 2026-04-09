#!/usr/bin/env python3
"""Echo Agent - for testing."""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from pathlib import Path

from agora.agent.base import AgentBase
from agora.protocol.message import Message


class EchoAgent(AgentBase):
    """Echo agent that returns received messages."""

    async def handle_message(self, message: Message) -> Message | None:
        """Echo the message back."""
        print(f"Received: {message.payload}")

        return Message(
            msg_id=str(uuid.uuid4()),
            from_agent=self.context.agent_id,
            to_agent=message.from_agent,
            capability="echo.response",
            payload={
                "echo": message.payload,
                "received_at": datetime.utcnow().isoformat()
            }
        )


async def main():
    manifest_path = Path(__file__).parent / "manifest.yaml"
    agent = EchoAgent(str(manifest_path))

    try:
        await agent.start()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
