#!/usr/bin/env python3
"""
L1 Observer Agent (Migration Notice)

The OpenCode-based autonomous observer has been migrated to a Claude Code Skill.
This script now serves as a thin compatibility layer that:
1. Performs a fast idempotency check
2. Prints a migration notice instructing the user to run the skill
"""
import os
import sys
from datetime import datetime

ROOT_DIR = "/Users/dr4/WorkSpace/context-infrastructure"
OBSERVATIONS_PATH = os.path.join(ROOT_DIR, "contexts", "memory", "OBSERVATIONS.md")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='L1 Observer Agent (Claude Code native)')
    parser.add_argument('date', nargs='?', default=datetime.now().strftime("%Y-%m-%d"),
                        help='Target date (YYYY-MM-DD)')
    args = parser.parse_args()

    target_date = args.date

    # Fast-path idempotency check
    if os.path.exists(OBSERVATIONS_PATH):
        with open(OBSERVATIONS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        if f"Date: {target_date}" in content:
            print(f"Idempotent skip: entry for {target_date} already exists in OBSERVATIONS.md")
            sys.exit(0)

    print("=" * 60)
    print("Observer has been migrated to a Claude Code Skill")
    print("=" * 60)
    print()
    print(f"To perform the L1 Observer scan for {target_date}, please run:")
    print()
    print("  /heartbeat-observer")
    print()
    print("Or invoke the Skill tool directly in a Claude Code session:")
    print()
    print('  Skill("heartbeat-observer")')
    print()
    print("The skill will execute the full scan directly using Claude Code's")
    print("native toolchain (no external OpenCode server required).")
    print("=" * 60)


if __name__ == "__main__":
    main()
