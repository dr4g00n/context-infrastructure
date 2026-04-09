import { z } from "zod"

// Tool 参数 Schema（使用 z.custom 避免循环引用类型推断问题）
export type ToolParameterType = {
  type: string
  description?: string
  enum?: string[]
  properties?: Record<string, ToolParameterType>
  required?: string[]
  items?: ToolParameterType
}

export const ToolParameterSchema: z.ZodType<ToolParameterType> = z.object({
  type: z.string(),
  description: z.string().optional(),
  enum: z.array(z.string()).optional(),
  properties: z.record(z.lazy(() => ToolParameterSchema)).optional(),
  required: z.array(z.string()).optional(),
  items: z.lazy(() => ToolParameterSchema).optional(),
})

// Tool Schema
export const ToolSchema = z.object({
  name: z.string().min(1, "工具名称不能为空"),
  description: z.string().min(1, "工具描述不能为空"),
  parameters: ToolParameterSchema.optional(),
  required_permissions: z.array(z.string()).default([]),
})

// Integration Auth Schema
export const IntegrationAuthSchema = z.object({
  type: z.enum(["none", "api_key", "oauth", "bearer", "basic"]),
  description: z.string().optional(),
})

// Integration Schema
export const IntegrationSchema = z.object({
  type: z.enum(["mcp", "api", "webhook", "websocket", "other"]),
  endpoint: z.string().url("请输入有效的 URL").optional(),
  auth: IntegrationAuthSchema.optional(),
  config: z.record(z.any()).optional(),
})

// AgentCard V1 完整 Schema
export const AgentCardSchema = z.object({
  $schema: z.string().default("https://agentcard.dev/schema/v1"),
  id: z.string().min(1, "ID 不能为空"),
  name: z.string().min(1, "名称不能为空"),
  version: z.string().regex(/^\d+\.\d+\.\d+$/, "版本号格式应为 x.y.z"),
  description: z.string().min(1, "描述不能为空"),
  author: z.string().optional(),
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),

  capabilities: z.object({
    reasoning: z.array(z.enum(["logical", "creative", "analytical", "critical", "spatial", "temporal"])).default([]),
    domain_expertise: z.array(z.string()).default([]),
    languages: z.array(z.string()).default(["zh", "en"]),
    context_window: z.number().positive().optional(),
    max_tokens_per_request: z.number().positive().optional(),
    supports_vision: z.boolean().default(false),
    supports_audio: z.boolean().default(false),
    supports_streaming: z.boolean().default(true),
  }).default({}),

  tools: z.array(ToolSchema).default([]),

  permissions: z.object({
    filesystem: z.array(z.enum(["read", "write", "delete", "execute"])).default([]),
    network: z.array(z.enum(["http_request", "websocket", "tcp", "udp"])).default([]),
    execution: z.array(z.enum(["bash", "python", "javascript", "docker", "sandbox"])).default([]),
    browser: z.array(z.enum(["navigation", "screenshot", "interaction", "download"])).default([]),
  }).default({}),

  constraints: z.object({
    max_tokens_per_request: z.number().positive().optional(),
    rate_limit: z.string().optional(),
    timeout: z.string().optional(),
    max_file_size: z.string().optional(),
    allowed_domains: z.array(z.string()).optional(),
    blocked_domains: z.array(z.string()).optional(),
  }).default({}),

  integrations: z.array(IntegrationSchema).default([]),

  metadata: z.object({
    tags: z.array(z.string()).default([]),
    category: z.enum(["assistant", "coding", "writing", "analysis", "creative", "research", "other"]).default("other"),
    license: z.string().default("MIT"),
    homepage: z.string().url().optional(),
    repository: z.string().url().optional(),
  }).default({}),
})

// Type 导出
export type AgentCard = z.infer<typeof AgentCardSchema>
export type Tool = z.infer<typeof ToolSchema>
export type Integration = z.infer<typeof IntegrationSchema>
export type ToolParameter = z.infer<typeof ToolParameterSchema>
export type IntegrationAuth = z.infer<typeof IntegrationAuthSchema>
