import pytest
from datetime import datetime
from hub.registry import AgentRegistry, AgentInfo


class TestAgentRegistry:
    def test_register_agent(self):
        reg = AgentRegistry()
        reg.register(
            agent_id="agent_1",
            api_key="key123",
            capabilities=["math.add"],
            endpoint="mqtt://hub:1883"
        )

        agent = reg.get("agent_1")
        assert agent is not None
        assert agent.agent_id == "agent_1"
        assert agent.capabilities == ["math.add"]

    def test_find_by_capability(self):
        reg = AgentRegistry()
        reg.register("agent_1", "key1", ["math.add", "math.sub"], "mqtt://hub:1883")
        reg.register("agent_2", "key2", ["math.multiply"], "mqtt://hub:1883")
        reg.register("agent_3", "key3", ["string.concat"], "mqtt://hub:1883")

        matches = reg.find_by_capability("math.*")
        assert len(matches) == 2
        assert all("math" in cap for agent in matches for cap in agent.capabilities)

    def test_unregister_agent(self):
        reg = AgentRegistry()
        reg.register("agent_1", "key1", ["math.add"], "mqtt://hub:1883")
        reg.unregister("agent_1")

        assert reg.get("agent_1") is None

    def test_update_heartbeat(self):
        reg = AgentRegistry()
        reg.register("agent_1", "key1", ["math.add"], "mqtt://hub:1883")

        old_time = reg.get("agent_1").last_heartbeat
        reg.update_heartbeat("agent_1")

        new_time = reg.get("agent_1").last_heartbeat
        assert new_time > old_time

    def test_get_stale_agents(self):
        reg = AgentRegistry()
        reg.register("agent_1", "key1", ["math.add"], "mqtt://hub:1883")
        # Simulate old heartbeat
        reg._agents["agent_1"].last_heartbeat = datetime.utcnow().timestamp() - 120

        stale = reg.get_stale_agents(timeout_seconds=60)
        assert len(stale) == 1
        assert stale[0] == "agent_1"
