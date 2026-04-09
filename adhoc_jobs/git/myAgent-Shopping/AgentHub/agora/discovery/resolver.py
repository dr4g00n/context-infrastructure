"""Client-side capability discovery."""
from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agora.protocol.transport import MqttTransport


class CapabilityResolver:
    """Client for discovering capabilities."""

    def __init__(self, transport: MqttTransport, agent_id: str) -> None:
        self.transport = transport
        self.agent_id = agent_id
        self._pending_responses: dict[str, asyncio.Future] = {}
        self._subscribed = False

    async def _ensure_subscribed(self) -> None:
        """Subscribe to inbox for discovery responses."""
        if not self._subscribed:
            inbox_topic = f"agora/agent/{self.agent_id}/inbox"
            await self.transport._client.subscribe(inbox_topic)
            self._subscribed = True

    async def discover(self, capability: str) -> list[dict]:
        """Discover agents with given capability."""
        await self._ensure_subscribed()

        message = {
            "agent_id": self.agent_id,
            "capability": capability
        }

        future = asyncio.get_event_loop().create_future()
        self._pending_responses[capability] = future

        # Start background listener for responses
        listener_task = asyncio.create_task(self._listen_for_response(capability))

        await self.transport._client.publish(
            "agora/hub/discover",
            payload=json.dumps(message).encode()
        )

        try:
            response = await asyncio.wait_for(future, timeout=5.0)
            listener_task.cancel()
            return response.get("agents", [])
        except asyncio.TimeoutError:
            listener_task.cancel()
            return []

    async def _listen_for_response(self, capability: str) -> None:
        """Listen for discovery response on inbox."""
        try:
            async for message in self.transport._client.messages:
                try:
                    payload = json.loads(message.payload.decode())
                    if payload.get("type") == "discovery_response" and payload.get("capability") == capability:
                        self.handle_response(payload)
                        break
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
        except asyncio.CancelledError:
            pass

    def handle_response(self, response: dict) -> None:
        """Handle discovery response."""
        capability = response.get("capability")
        if capability in self._pending_responses:
            future = self._pending_responses.pop(capability)
            if not future.done():
                future.set_result(response)
