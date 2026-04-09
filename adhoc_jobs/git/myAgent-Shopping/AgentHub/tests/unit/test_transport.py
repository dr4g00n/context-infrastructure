import pytest
from unittest.mock import Mock, patch, AsyncMock
from agora.protocol.transport import MqttTransport
from agora.protocol.message import Message


class TestMqttTransport:
    @pytest.mark.asyncio
    async def test_connect(self):
        with patch('aiomqtt.Client') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)

            transport = MqttTransport(host="localhost", port=1883)
            await transport.connect()

            assert transport.is_connected is True

    @pytest.mark.asyncio
    async def test_subscribe(self):
        with patch('aiomqtt.Client') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)

            transport = MqttTransport(host="localhost", port=1883)
            await transport.connect()
            await transport.subscribe("agora/agent/test/inbox")

            mock_instance.subscribe.assert_called_once_with("agora/agent/test/inbox")

    @pytest.mark.asyncio
    async def test_publish(self):
        with patch('aiomqtt.Client') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)

            transport = MqttTransport(host="localhost", port=1883)
            await transport.connect()

            msg = Message(
                msg_id="test-id",
                from_agent="a",
                to_agent="b",
                capability="test",
                payload={"key": "value"}
            )
            await transport.publish("agora/agent/b/inbox", msg)

            mock_instance.publish.assert_called_once()
