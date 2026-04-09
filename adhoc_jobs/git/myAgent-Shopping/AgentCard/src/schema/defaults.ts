import type { AgentCard, Tool, Integration } from "./agentcard-v1"

export const defaultTool = (): Tool => ({
  name: "",
  description: "",
  parameters: {
    type: "object",
    properties: {},
    required: [],
  },
  required_permissions: [],
})

export const defaultIntegration = (): Integration => ({
  type: "mcp",
  endpoint: "",
  auth: {
    type: "none",
  },
})

export const exampleAgentCard: AgentCard = {
  $schema: "https://agentcard.dev/schema/v1",
  id: "agent-code-assistant-001",
  name: "代码助手",
  version: "2.1.0",
  description: "专业的编程助手，擅长代码审查、重构建议和调试辅助",
  author: "DevTeam",
  created_at: "2024-01-15T08:00:00Z",
  updated_at: "2024-03-20T12:30:00Z",

  capabilities: {
    reasoning: ["logical", "analytical", "critical"],
    domain_expertise: ["programming", "software_architecture", "debugging"],
    languages: ["zh", "en", "ja"],
    context_window: 200000,
    max_tokens_per_request: 8192,
    supports_vision: true,
    supports_audio: false,
    supports_streaming: true,
  },

  tools: [
    {
      name: "read_file",
      description: "读取指定路径的文件内容",
      parameters: {
        type: "object",
        properties: {
          path: {
            type: "string",
            description: "文件路径",
          },
          offset: {
            type: "number",
            description: "起始行号",
          },
          limit: {
            type: "number",
            description: "读取行数",
          },
        },
        required: ["path"],
      },
      required_permissions: ["read"],
    },
    {
      name: "search_code",
      description: "在代码库中搜索指定模式",
      parameters: {
        type: "object",
        properties: {
          pattern: {
            type: "string",
            description: "搜索模式",
          },
          glob: {
            type: "string",
            description: "文件匹配模式",
          },
        },
        required: ["pattern"],
      },
      required_permissions: ["read"],
    },
  ],

  permissions: {
    filesystem: ["read", "write"],
    network: ["http_request"],
    execution: ["bash", "python"],
    browser: [],
  },

  constraints: {
    max_tokens_per_request: 8192,
    rate_limit: "60/min",
    timeout: "60s",
    max_file_size: "10MB",
  },

  integrations: [
    {
      type: "mcp",
      endpoint: "http://localhost:3000/mcp",
      auth: {
        type: "bearer",
      },
    },
  ],

  metadata: {
    tags: ["coding", "assistant", "developer-tools"],
    category: "coding",
    license: "MIT",
    homepage: "https://example.com/agent/code-assistant",
    repository: "https://github.com/example/code-assistant",
  },
}

export const categoryOptions = [
  { value: "assistant", label: "通用助手" },
  { value: "coding", label: "编程开发" },
  { value: "writing", label: "写作创作" },
  { value: "analysis", label: "数据分析" },
  { value: "creative", label: "创意设计" },
  { value: "research", label: "研究调研" },
  { value: "other", label: "其他" },
]

export const reasoningOptions = [
  { value: "logical", label: "逻辑推理" },
  { value: "creative", label: "创造性思维" },
  { value: "analytical", label: "分析思维" },
  { value: "critical", label: "批判性思维" },
  { value: "spatial", label: "空间推理" },
  { value: "temporal", label: "时序推理" },
]

export const languageOptions = [
  { value: "zh", label: "中文" },
  { value: "en", label: "英语" },
  { value: "ja", label: "日语" },
  { value: "ko", label: "韩语" },
  { value: "es", label: "西班牙语" },
  { value: "fr", label: "法语" },
  { value: "de", label: "德语" },
  { value: "ru", label: "俄语" },
  { value: "ar", label: "阿拉伯语" },
  { value: "pt", label: "葡萄牙语" },
  { value: "it", label: "意大利语" },
]
