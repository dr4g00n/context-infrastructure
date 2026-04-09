#!/usr/bin/env python3
"""Basic discovery example - find agents with capabilities."""
import asyncio
from agora.protocol.transport import MqttTransport
from agora.discovery.resolver import CapabilityResolver


async def main():
    transport = MqttTransport("localhost", 1883)
    await transport.connect()

    resolver = CapabilityResolver(transport, "test_client")

    print("Discovering math agents...")
    agents = await resolver.discover("math.*")

    print(f"Found {len(agents)} agents:")
    for agent in agents:
        print(f"  - {agent['id']}")

    await transport.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
