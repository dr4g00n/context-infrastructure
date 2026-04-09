import pytest
from agora.agent.capability import Capability, CapabilityRegistry


class TestCapability:
    def test_capability_creation(self):
        cap = Capability(
            name="math.add",
            description="Add two numbers",
            input_schema={"type": "object", "properties": {"a": {"type": "number"}}},
            output_schema={"type": "object", "properties": {"result": {"type": "number"}}}
        )
        assert cap.name == "math.add"
        assert cap.description == "Add two numbers"

    def test_capability_matches_exact(self):
        cap = Capability(name="math.add", description="Add")
        assert cap.matches("math.add") is True
        assert cap.matches("math.subtract") is False

    def test_capability_matches_wildcard(self):
        cap = Capability(name="math.add", description="Add")
        assert cap.matches("math.*") is True
        assert cap.matches("*.add") is True
        assert cap.matches("*") is True
        assert cap.matches("calc.*") is False


class TestCapabilityRegistry:
    def test_add_capability(self):
        reg = CapabilityRegistry()
        cap = Capability(name="math.add", description="Add")
        reg.add(cap)
        assert len(reg.list_all()) == 1

    def test_find_by_pattern(self):
        reg = CapabilityRegistry()
        reg.add(Capability(name="math.add", description="Add"))
        reg.add(Capability(name="math.multiply", description="Multiply"))
        reg.add(Capability(name="string.concat", description="Concat"))

        matches = reg.find("math.*")
        assert len(matches) == 2
        assert all(m.name.startswith("math.") for m in matches)

    def test_find_by_exact(self):
        reg = CapabilityRegistry()
        reg.add(Capability(name="math.add", description="Add"))

        matches = reg.find("math.add")
        assert len(matches) == 1
        assert matches[0].name == "math.add"
