#!/usr/bin/env python3
"""
L2 Reflector Agent (Migration Notice)

The OpenCode-based autonomous reflector has been migrated to a Claude Code Skill.
This script now serves as a thin compatibility layer that prints a migration notice.
"""
import sys
from datetime import datetime


def main():
    print("=" * 60)
    print("Reflector has been migrated to a Claude Code Skill")
    print("=" * 60)
    print()
    print("To perform the L2 Reflector analysis and rule promotion,")
    print("please run the following command in a Claude Code session:")
    print()
    print("  /heartbeat-reflector")
    print()
    print("Or invoke the Skill tool directly:")
    print()
    print('  Skill("heartbeat-reflector")')
    print()
    print("The skill will:")
    print("  1. Analyze contexts/memory/OBSERVATIONS.md")
    print("  2. Generate structured proposals in")
    print("     contexts/memory/PENDING_RULES_PROPOSALS.md")
    print("  3. Wait for your confirmation before modifying any")
    print("     rules/ files (per CLAUDE.md evolution loop)")
    print("=" * 60)


if __name__ == "__main__":
    main()
