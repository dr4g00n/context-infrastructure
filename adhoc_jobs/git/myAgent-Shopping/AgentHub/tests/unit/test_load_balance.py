import pytest
from agora.routing.load_balance import LeastConnectionsStrategy
from hub.registry import AgentInfo


class TestLeastConnectionsStrategy:
    def test_select_single_agent(self):
        strategy = LeastConnectionsStrategy()
        agents = [
            AgentInfo("agent_1", "key1", ["math.add"], "mqtt://hub:1883", active_connections=5)
        ]

        selected = strategy.select(agents)
        assert selected == "agent_1"

    def test_select_least_connections(self):
        strategy = LeastConnectionsStrategy()
        agents = [
            AgentInfo("agent_1", "key1", ["math.add"], "mqtt://hub:1883", active_connections=5),
            AgentInfo("agent_2", "key2", ["math.add"], "mqtt://hub:1883", active_connections=2),
            AgentInfo("agent_3", "key3", ["math.add"], "mqtt://hub:1883", active_connections=8),
        ]

        selected = strategy.select(agents)
        assert selected == "agent_2"

    def test_select_empty_list(self):
        strategy = LeastConnectionsStrategy()
        selected = strategy.select([])
        assert selected is None

    def test_select_tie_break(self):
        strategy = LeastConnectionsStrategy()
        agents = [
            AgentInfo("agent_1", "key1", ["math.add"], "mqtt://hub:1883", active_connections=2),
            AgentInfo("agent_2", "key2", ["math.add"], "mqtt://hub:1883", active_connections=2),
        ]

        selected = strategy.select(agents)
        assert selected in ["agent_1", "agent_2"]
