# Agora Architecture

## Overview

Agora is a hub-based Agent coordination platform using MQTT for transport.

## Components

### Hub
- MQTT Broker integration
- In-memory Agent registry
- Message queue with TTL
- Heartbeat monitoring

### Agent SDK
- Base class for Agent development
- Capability declaration
- Message routing
- Discovery client

## Message Flow

1. Agent connects to Hub via MQTT
2. Agent registers with capabilities
3. Hub maintains registry and routes messages
4. Messages queued with TTL for offline agents
