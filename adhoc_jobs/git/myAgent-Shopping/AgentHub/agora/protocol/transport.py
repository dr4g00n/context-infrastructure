"""MQTT transport layer abstraction."""
from __future__ import annotations

import asyncio
from typing import Callable

import aiomqtt
from agora.protocol.message import Message
from agora.protocol.codec import MessageCodec


class MqttTransport:
    """Async MQTT transport for Agent communication."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 1883,
        keepalive: int = 60
    ) -> None:
        self.host = host
        self.port = port
        self.keepalive = keepalive
        self._client: aiomqtt.Client | None = None
        self._message_handler: Callable[[Message], None] | None = None
        self._task: asyncio.Task | None = None

    @property
    def is_connected(self) -> bool:
        """Check if transport is connected."""
        return self._client is not None

    async def connect(self) -> None:
        """Connect to MQTT broker."""
        self._client = aiomqtt.Client(
            hostname=self.host,
            port=self.port,
            keepalive=self.keepalive
        )
        await self._client.__aenter__()

    async def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        if self._client:
            await self._client.__aexit__(None, None, None)
            self._client = None

    async def subscribe(self, topic: str) -> None:
        """Subscribe to a topic."""
        if not self._client:
            raise RuntimeError("Not connected")
        await self._client.subscribe(topic)

    async def publish(self, topic: str, message: Message, qos: int = 1) -> None:
        """Publish a message to a topic."""
        if not self._client:
            raise RuntimeError("Not connected")
        payload = MessageCodec.encode(message)
        await self._client.publish(topic, payload=payload, qos=qos)

    def on_message(self, handler: Callable[[Message], None]) -> None:
        """Set message handler callback."""
        self._message_handler = handler

    async def start_message_loop(self) -> None:
        """Start receiving messages."""
        if not self._client:
            raise RuntimeError("Not connected")

        async for message in self._client.messages:
            if self._message_handler:
                try:
                    decoded = MessageCodec.decode(message.payload)
                    self._message_handler(decoded)
                except Exception as e:
                    print(f"Failed to decode message: {e}")
