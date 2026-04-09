import pytest


@pytest.mark.asyncio
async def test_capability_routing():
    """Test messages route to correct capability."""
    pytest.skip("Requires running Hub - run manually")
