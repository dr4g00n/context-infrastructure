#!/usr/bin/env python3
"""Calculator Agent - performs math operations."""
from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

from agora.agent.base import AgentBase
from agora.protocol.message import Message


class CalculatorAgent(AgentBase):
    """Calculator agent for math operations."""

    async def handle_message(self, message: Message) -> Message | None:
        """Handle math operations."""
        cap = message.capability
        payload = message.payload

        if cap == "math.add":
            result = payload["a"] + payload["b"]
        elif cap == "math.subtract":
            result = payload["a"] - payload["b"]
        elif cap == "math.multiply":
            result = payload["a"] * payload["b"]
        elif cap == "math.divide":
            if payload["b"] == 0:
                result = {"error": "Division by zero"}
            else:
                result = payload["a"] / payload["b"]
        else:
            return None

        return Message(
            msg_id=str(uuid.uuid4()),
            from_agent=self.context.agent_id,
            to_agent=message.from_agent,
            capability=f"{cap}.response",
            payload={"result": result}
        )


async def main():
    manifest_path = Path(__file__).parent / "manifest.yaml"
    agent = CalculatorAgent(str(manifest_path))

    try:
        await agent.start()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
