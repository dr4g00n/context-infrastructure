"""Agent runtime context."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agora.agent.capability import CapabilityRegistry


@dataclass
class AgentContext:
    """Runtime context for an Agent."""
    agent_id: str
    hub_host: str = "localhost"
    hub_port: int = 1883
    capabilities: CapabilityRegistry = field(default_factory=CapabilityRegistry)
    state: dict[str, Any] = field(default_factory=dict)
