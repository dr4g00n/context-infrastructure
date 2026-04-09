#!/usr/bin/env python3
import asyncio
import json
import aiomqtt
from datetime import datetime, UTC

async def main():
    client = aiomqtt.Client("localhost", 1883)
    await client.__aenter__()
    
    # Send message (codec format)
    msg = {
        "msg_id": "test-001",
        "from": "test_client",
        "to": "echo_agent",
        "capability": "echo.send",
        "payload": {"message": "Hello Agora!"},
        "timestamp": datetime.now(UTC).isoformat(),
        "ttl": 300
    }
    
    await client.publish("agora/agent/echo_agent/inbox", 
                        payload=json.dumps(msg).encode())
    print(f"[SENT] {msg['payload']}")
    
    # Wait for response
    await client.subscribe("agora/agent/test_client/inbox")
    print("[WAITING] for response...")
    
    try:
        async for message in client.messages:
            payload = json.loads(message.payload.decode())
            print(f"[RECEIVED] {payload}")
            break
    except asyncio.TimeoutError:
        print("[TIMEOUT] No response received")
    
    await client.__aexit__(None, None, None)

if __name__ == "__main__":
    asyncio.run(main())
