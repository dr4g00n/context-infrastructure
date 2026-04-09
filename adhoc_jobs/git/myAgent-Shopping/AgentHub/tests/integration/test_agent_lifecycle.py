import pytest
import asyncio
from agora.protocol.message import Message


@pytest.mark.asyncio
async def test_agent_registration_flow():
    """Test agent can register and unregister."""
    # This test requires running Hub
    # Skip if Hub not available
    pytest.skip("Requires running Hub - run manually")


@pytest.mark.asyncio
async def test_message_echo():
    """Test echo agent responds correctly."""
    pytest.skip("Requires running Hub and Echo Agent - run manually")
