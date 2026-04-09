import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import type { AgentCard } from "@/schema/agentcard-v1"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function generateId(): string {
  return `agent-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

export function formatDate(date: Date = new Date()): string {
  return date.toISOString()
}

export function defaultAgentCard(): AgentCard {
  return {
    $schema: "https://agentcard.dev/schema/v1",
    id: generateId(),
    name: "",
    version: "1.0.0",
    description: "",
    author: "",
    created_at: formatDate(),
    updated_at: formatDate(),

    capabilities: {
      reasoning: ["logical", "analytical"],
      domain_expertise: [],
      languages: ["zh", "en"],
      context_window: 128000,
      max_tokens_per_request: 4096,
      supports_vision: false,
      supports_audio: false,
      supports_streaming: true,
    },

    tools: [],

    permissions: {
      filesystem: ["read"],
      network: ["http_request"],
      execution: [],
      browser: [],
    },

    constraints: {
      max_tokens_per_request: 4096,
      rate_limit: "100/min",
      timeout: "30s",
    },

    integrations: [],

    metadata: {
      tags: [],
      category: "assistant",
      license: "MIT",
    },
  }
}
