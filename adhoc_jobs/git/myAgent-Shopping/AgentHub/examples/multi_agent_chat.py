#!/usr/bin/env python3
"""Multi-agent chat example."""
import asyncio
import uuid
from agora.protocol.transport import MqttTransport
from agora.protocol.message import Message


async def main():
    transport = MqttTransport("localhost", 1883)
    await transport.connect()

    # Send message to echo agent
    msg = Message(
        msg_id=str(uuid.uuid4()),
        from_agent="chat_client",
        to_agent="echo_agent",
        capability="echo.send",
        payload={"message": "Hello from chat!"}
    )

    await transport.publish("agora/agent/echo_agent/inbox", msg)
    print("Message sent to echo agent")

    await asyncio.sleep(1)
    await transport.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
