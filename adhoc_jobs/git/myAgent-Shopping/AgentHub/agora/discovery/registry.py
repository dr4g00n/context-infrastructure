"""Client-side Agent registration."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agora.protocol.transport import MqttTransport


class AgentRegistryClient:
    """Client for registering with Hub."""

    def __init__(self, transport: MqttTransport, agent_id: str, api_key: str) -> None:
        self.transport = transport
        self.agent_id = agent_id
        self.api_key = api_key

    async def register(self, capabilities: list[str], endpoint: str) -> None:
        """Register with Hub."""
        message = {
            "type": "register",
            "agent_id": self.agent_id,
            "api_key": self.api_key,
            "capabilities": capabilities,
            "endpoint": endpoint
        }
        # Note: publish expects Message object, need to fix this
        # For now, use raw MQTT publish via client
        await self.transport._client.publish(
            "agora/hub/registry",
            payload=json.dumps(message).encode()
        )

    async def unregister(self) -> None:
        """Unregister from Hub."""
        message = {
            "type": "unregister",
            "agent_id": self.agent_id
        }
        await self.transport._client.publish(
            "agora/hub/registry",
            payload=json.dumps(message).encode()
        )

    async def send_heartbeat(self) -> None:
        """Send heartbeat to Hub."""
        message = {
            "agent_id": self.agent_id,
            "timestamp": json.dumps({})  # Placeholder
        }
        await self.transport._client.publish(
            "agora/hub/heartbeat",
            payload=json.dumps(message).encode()
        )
