#!/usr/bin/env python3
"""Agora Hub - Central coordination service."""
from __future__ import annotations

import asyncio
import json
import signal
import sys
from pathlib import Path

import aiomqtt
import yaml
from agora.protocol.message import Message
from agora.protocol.codec import MessageCodec
from agora.routing.load_balance import LeastConnectionsStrategy
from hub.registry import AgentRegistry
from hub.msg_queue import MessageQueueManager


class AgoraHub:
    """Main Hub service coordinating Agent communication."""

    def __init__(self, config_path: str = "hub/config.yaml") -> None:
        with open(config_path) as f:
            self.config = yaml.safe_load(f)["hub"]

        self.registry = AgentRegistry()
        self.queue_manager = MessageQueueManager(
            ttl_seconds=self.config["queue"]["ttl_seconds"],
            max_size=self.config["queue"]["max_size_per_agent"]
        )
        self.load_balancer = LeastConnectionsStrategy()
        self._shutdown_event = asyncio.Event()
        self._tasks: list[asyncio.Task] = []

    async def run(self) -> None:
        """Run the Hub service."""
        print(f"Starting Agora Hub on {self.config['mqtt']['host']}:{self.config['mqtt']['port']}")

        # Start background tasks
        self._tasks.append(asyncio.create_task(self._cleanup_loop()))
        self._tasks.append(asyncio.create_task(self._heartbeat_check_loop()))

        async with aiomqtt.Client(
            hostname=self.config["mqtt"]["host"],
            port=self.config["mqtt"]["port"]
        ) as client:
            # Subscribe to Hub topics
            await client.subscribe("agora/hub/registry")
            await client.subscribe("agora/hub/heartbeat")
            await client.subscribe("agora/hub/discover")

            print("Hub ready. Waiting for messages...")

            async for message in client.messages:
                if self._shutdown_event.is_set():
                    break
                await self._handle_message(client, message)

    async def _handle_message(self, client: aiomqtt.Client, message: aiomqtt.Message) -> None:
        """Handle incoming MQTT message."""
        topic = str(message.topic)

        try:
            payload = json.loads(message.payload.decode())
        except json.JSONDecodeError:
            print(f"Invalid JSON on {topic}")
            return

        if "registry" in topic:
            await self._handle_registry(client, payload)
        elif "heartbeat" in topic:
            await self._handle_heartbeat(payload)
        elif "discover" in topic:
            await self._handle_discover(client, payload)

    async def _handle_registry(self, client: aiomqtt.Client, payload: dict) -> None:
        """Handle agent registration."""
        msg_type = payload.get("type")
        agent_id = payload.get("agent_id")

        if msg_type == "register":
            self.registry.register(
                agent_id=agent_id,
                api_key=payload.get("api_key"),
                capabilities=payload.get("capabilities", []),
                endpoint=payload.get("endpoint", "")
            )
            print(f"Agent registered: {agent_id}")

            # Broadcast online event
            await client.publish(
                "agora/hub/events",
                json.dumps({"type": "agent_online", "agent_id": agent_id}).encode()
            )

        elif msg_type == "unregister":
            self.registry.unregister(agent_id)
            self.queue_manager.clear_queue(agent_id)
            print(f"Agent unregistered: {agent_id}")

            await client.publish(
                "agora/hub/events",
                json.dumps({"type": "agent_offline", "agent_id": agent_id}).encode()
            )

    async def _handle_heartbeat(self, payload: dict) -> None:
        """Handle agent heartbeat."""
        agent_id = payload.get("agent_id")
        if self.registry.update_heartbeat(agent_id):
            print(f"Heartbeat from: {agent_id}")

    async def _handle_discover(self, client: aiomqtt.Client, payload: dict) -> None:
        """Handle capability discovery request."""
        capability = payload.get("capability")
        requester = payload.get("agent_id")

        matches = self.registry.find_by_capability(capability)
        if matches:
            # Select using load balancer
            selected_id = self.load_balancer.select(matches)
            if selected_id:
                self.registry.increment_connections(selected_id)

                # Send response
                response = {
                    "type": "discovery_response",
                    "capability": capability,
                    "agents": [{"id": selected_id}]
                }
                await client.publish(
                    f"agora/agent/{requester}/inbox",
                    json.dumps(response).encode()
                )

    async def _cleanup_loop(self) -> None:
        """Periodic cleanup of expired messages."""
        while not self._shutdown_event.is_set():
            await asyncio.sleep(self.config["queue"]["cleanup_interval"])
            removed = self.queue_manager.cleanup_expired()
            if removed > 0:
                print(f"Cleaned up {removed} expired messages")

    async def _heartbeat_check_loop(self) -> None:
        """Check for stale agents."""
        while not self._shutdown_event.is_set():
            await asyncio.sleep(self.config["heartbeat"]["check_interval"])
            stale = self.registry.get_stale_agents(
                self.config["heartbeat"]["timeout_seconds"]
            )
            for agent_id in stale:
                print(f"Agent timeout: {agent_id}")
                self.registry.unregister(agent_id)
                self.queue_manager.clear_queue(agent_id)

    def shutdown(self) -> None:
        """Signal shutdown."""
        print("Shutting down...")
        self._shutdown_event.set()
        for task in self._tasks:
            task.cancel()


def main():
    hub = AgoraHub()

    def signal_handler(sig, frame):
        hub.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    asyncio.run(hub.run())


if __name__ == "__main__":
    main()
