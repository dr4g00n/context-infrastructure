"""Base Agent class."""
from __future__ import annotations

import asyncio
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import yaml
from agora.protocol.message import Message
from agora.protocol.transport import MqttTransport
from agora.agent.context import AgentContext
from agora.agent.capability import Capability, CapabilityRegistry
from agora.discovery.registry import AgentRegistryClient
from agora.discovery.resolver import CapabilityResolver


class AgentBase(ABC):
    """Base class for all Agents."""

    def __init__(
        self,
        manifest_path: str,
        hub_host: str = "localhost",
        hub_port: int = 1883
    ) -> None:
        self.manifest = self._load_manifest(manifest_path)
        self.context = AgentContext(
            agent_id=self.manifest["agent"]["id"],
            hub_host=hub_host,
            hub_port=hub_port,
            capabilities=self._load_capabilities()
        )
        self.transport = MqttTransport(host=hub_host, port=hub_port)
        self.registry_client = AgentRegistryClient(
            self.transport,
            self.context.agent_id,
            self.manifest["agent"]["api_key"]
        )
        self.resolver = CapabilityResolver(self.transport, self.context.agent_id)
        self._running = False
        self._heartbeat_task: asyncio.Task | None = None

    def _load_manifest(self, path: str) -> dict:
        """Load agent manifest from YAML."""
        with open(path) as f:
            return yaml.safe_load(f)

    def _load_capabilities(self) -> CapabilityRegistry:
        """Load capabilities from manifest."""
        registry = CapabilityRegistry()
        for cap_data in self.manifest.get("capabilities", []):
            cap = Capability(
                name=cap_data["name"],
                description=cap_data.get("description", ""),
                input_schema=cap_data.get("input_schema"),
                output_schema=cap_data.get("output_schema")
            )
            registry.add(cap)
        return registry

    async def start(self) -> None:
        """Start the agent."""
        await self.transport.connect()

        # Subscribe to inbox
        inbox_topic = f"agora/agent/{self.context.agent_id}/inbox"
        await self.transport.subscribe(inbox_topic)
        self.transport.on_message(self._on_message)

        # Register with Hub
        capabilities = [c.name for c in self.context.capabilities.list_all()]
        await self.registry_client.register(
            capabilities=capabilities,
            endpoint=f"mqtt://{self.context.hub_host}:{self.context.hub_port}"
        )

        # Start heartbeat
        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        # Start message loop
        await self.transport.start_message_loop()

    async def stop(self) -> None:
        """Stop the agent."""
        self._running = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        await self.registry_client.unregister()
        await self.transport.disconnect()

    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeats."""
        while self._running:
            try:
                await self.registry_client.send_heartbeat()
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Heartbeat error: {e}")
                await asyncio.sleep(5)

    def _on_message(self, message: Message) -> None:
        """Handle incoming message."""
        asyncio.create_task(self._process_message(message))

    async def _process_message(self, message: Message) -> None:
        """Process and respond to message."""
        response = await self.handle_message(message)
        if response:
            await self.transport.publish(
                f"agora/agent/{message.from_agent}/inbox",
                response
            )

    @abstractmethod
    async def handle_message(self, message: Message) -> Message | None:
        """Handle a message. Override in subclass."""
        pass

    async def send_to_capability(
        self,
        capability: str,
        payload: dict[str, Any]
    ) -> None:
        """Send message to agents with given capability."""
        # Discover agents
        agents = await self.resolver.discover(capability)
        if not agents:
            print(f"No agents found for capability: {capability}")
            return

        target = agents[0]["id"]
        message = Message(
            msg_id=str(uuid.uuid4()),
            from_agent=self.context.agent_id,
            to_agent=target,
            capability=capability,
            payload=payload
        )

        await self.transport.publish(
            f"agora/agent/{target}/inbox",
            message
        )
