"""Capability declaration and matching."""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Capability:
    """An Agent capability declaration.

    Attributes:
        name: Dot-separated identifier (e.g., "math.add")
        description: Human-readable description
        input_schema: JSON Schema for input validation
        output_schema: JSON Schema for output validation
    """
    name: str
    description: str
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None

    def matches(self, pattern: str) -> bool:
        """Check if capability matches a pattern.

        Supports wildcards:
        - "math.*" matches "math.add", "math.subtract"
        - "*.add" matches "math.add", "calc.add"
        - "*" matches everything
        """
        return fnmatch.fnmatch(self.name, pattern)


class CapabilityRegistry:
    """Registry for managing multiple capabilities."""

    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}

    def add(self, capability: Capability) -> None:
        """Add a capability to the registry."""
        self._capabilities[capability.name] = capability

    def get(self, name: str) -> Capability | None:
        """Get capability by exact name."""
        return self._capabilities.get(name)

    def find(self, pattern: str) -> list[Capability]:
        """Find capabilities matching pattern."""
        return [cap for cap in self._capabilities.values() if cap.matches(pattern)]

    def list_all(self) -> list[Capability]:
        """List all registered capabilities."""
        return list(self._capabilities.values())

    def remove(self, name: str) -> None:
        """Remove a capability by name."""
        self._capabilities.pop(name, None)
