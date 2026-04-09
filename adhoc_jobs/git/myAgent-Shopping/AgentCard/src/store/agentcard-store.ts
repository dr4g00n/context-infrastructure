import { create } from "zustand"
import { persist } from "zustand/middleware"
import type { AgentCard, Tool, Integration } from "@/schema/agentcard-v1"
import { defaultAgentCard, formatDate } from "@/lib/utils"

interface AgentCardState {
  // 当前 AgentCard 数据
  agentCard: AgentCard
  // 验证错误
  validationErrors: string[]
  // 是否已修改
  isDirty: boolean

  // Actions
  setAgentCard: (agentCard: AgentCard) => void
  updateAgentCard: (updates: Partial<AgentCard>) => void
  updateCapabilities: (capabilities: Partial<AgentCard["capabilities"]>) => void
  updatePermissions: (permissions: Partial<AgentCard["permissions"]>) => void
  updateConstraints: (constraints: Partial<AgentCard["constraints"]>) => void
  updateMetadata: (metadata: Partial<AgentCard["metadata"]>) => void
  addTool: (tool: Tool) => void
  updateTool: (index: number, tool: Tool) => void
  removeTool: (index: number) => void
  addIntegration: (integration: Integration) => void
  updateIntegration: (index: number, integration: Integration) => void
  removeIntegration: (index: number) => void
  resetAgentCard: () => void
  loadExample: (example: AgentCard) => void
  setValidationErrors: (errors: string[]) => void
  markAsDirty: () => void
  updateTimestamp: () => void
}

export const useAgentCardStore = create<AgentCardState>()(
  persist(
    (set) => ({
      agentCard: defaultAgentCard(),
      validationErrors: [],
      isDirty: false,

      setAgentCard: (agentCard) => {
        set({ agentCard, isDirty: true })
      },

      updateAgentCard: (updates) => {
        set((state) => ({
          agentCard: { ...state.agentCard, ...updates },
          isDirty: true,
        }))
      },

      updateCapabilities: (capabilities) => {
        set((state) => ({
          agentCard: {
            ...state.agentCard,
            capabilities: { ...state.agentCard.capabilities, ...capabilities },
          },
          isDirty: true,
        }))
      },

      updatePermissions: (permissions) => {
        set((state) => ({
          agentCard: {
            ...state.agentCard,
            permissions: { ...state.agentCard.permissions, ...permissions },
          },
          isDirty: true,
        }))
      },

      updateConstraints: (constraints) => {
        set((state) => ({
          agentCard: {
            ...state.agentCard,
            constraints: { ...state.agentCard.constraints, ...constraints },
          },
          isDirty: true,
        }))
      },

      updateMetadata: (metadata) => {
        set((state) => ({
          agentCard: {
            ...state.agentCard,
            metadata: { ...state.agentCard.metadata, ...metadata },
          },
          isDirty: true,
        }))
      },

      addTool: (tool) => {
        set((state) => ({
          agentCard: {
            ...state.agentCard,
            tools: [...state.agentCard.tools, tool],
          },
          isDirty: true,
        }))
      },

      updateTool: (index, tool) => {
        set((state) => ({
          agentCard: {
            ...state.agentCard,
            tools: state.agentCard.tools.map((t, i) =>
              i === index ? tool : t
            ),
          },
          isDirty: true,
        }))
      },

      removeTool: (index) => {
        set((state) => ({
          agentCard: {
            ...state.agentCard,
            tools: state.agentCard.tools.filter((_, i) => i !== index),
          },
          isDirty: true,
        }))
      },

      addIntegration: (integration) => {
        set((state) => ({
          agentCard: {
            ...state.agentCard,
            integrations: [...state.agentCard.integrations, integration],
          },
          isDirty: true,
        }))
      },

      updateIntegration: (index, integration) => {
        set((state) => ({
          agentCard: {
            ...state.agentCard,
            integrations: state.agentCard.integrations.map((int, i) =>
              i === index ? integration : int
            ),
          },
          isDirty: true,
        }))
      },

      removeIntegration: (index) => {
        set((state) => ({
          agentCard: {
            ...state.agentCard,
            integrations: state.agentCard.integrations.filter((_, i) => i !== index),
          },
          isDirty: true,
        }))
      },

      resetAgentCard: () => {
        set({ agentCard: defaultAgentCard(), isDirty: false, validationErrors: [] })
      },

      loadExample: (example) => {
        set({ agentCard: example, isDirty: true, validationErrors: [] })
      },

      setValidationErrors: (errors) => {
        set({ validationErrors: errors })
      },

      markAsDirty: () => {
        set({ isDirty: true })
      },

      updateTimestamp: () => {
        set((state) => ({
          agentCard: {
            ...state.agentCard,
            updated_at: formatDate(),
          },
        }))
      },
    }),
    {
      name: "agentcard-storage",
      partialize: (state) => ({ agentCard: state.agentCard }),
    }
  )
)
