import { useState } from "react"
import { useAgentCardStore } from "@/store/agentcard-store"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Plus, Trash2, Edit2, Check, X } from "lucide-react"
import type { Integration, IntegrationAuth } from "@/schema/agentcard-v1"
import { defaultIntegration } from "@/schema/defaults"

const integrationTypes = [
  { value: "mcp", label: "MCP (Model Context Protocol)" },
  { value: "api", label: "API" },
  { value: "webhook", label: "Webhook" },
  { value: "websocket", label: "WebSocket" },
  { value: "other", label: "其他" },
]

const authTypes = [
  { value: "none", label: "无认证" },
  { value: "api_key", label: "API Key" },
  { value: "oauth", label: "OAuth" },
  { value: "bearer", label: "Bearer Token" },
  { value: "basic", label: "Basic Auth" },
]

export function IntegrationsForm() {
  const { agentCard, addIntegration, updateIntegration, removeIntegration, updateTimestamp } = useAgentCardStore()
  const [editingIndex, setEditingIndex] = useState<number | null>(null)
  const [editingIntegration, setEditingIntegration] = useState<Integration>(defaultIntegration())

  const handleAdd = () => {
    addIntegration(defaultIntegration())
    setEditingIndex(agentCard.integrations.length)
    setEditingIntegration(defaultIntegration())
    updateTimestamp()
  }

  const handleEdit = (index: number) => {
    setEditingIndex(index)
    setEditingIntegration({ ...agentCard.integrations[index] })
  }

  const handleSave = () => {
    if (editingIndex !== null) {
      updateIntegration(editingIndex, editingIntegration)
      setEditingIndex(null)
      updateTimestamp()
    }
  }

  const handleCancel = () => {
    setEditingIndex(null)
    setEditingIntegration(defaultIntegration())
  }

  const handleRemove = (index: number) => {
    removeIntegration(index)
    if (editingIndex === index) {
      setEditingIndex(null)
    }
    updateTimestamp()
  }

  const updateEditingIntegration = (field: keyof Integration, value: unknown) => {
    setEditingIntegration((prev) => ({ ...prev, [field]: value }))
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>集成配置</CardTitle>
        <Button onClick={handleAdd} size="sm" className="gap-1">
          <Plus className="h-4 w-4" />
          添加集成
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        {agentCard.integrations.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">
            暂无集成配置，点击上方按钮添加
          </p>
        ) : (
          <div className="space-y-3">
            {agentCard.integrations.map((integration, index) => (
              <div key={index} className="border rounded-lg p-4">
                {editingIndex === index ? (
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label>集成类型</Label>
                      <Select
                        value={editingIntegration.type}
                        onValueChange={(value) =>
                          updateEditingIntegration("type", value as Integration["type"])
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {integrationTypes.map((type) => (
                            <SelectItem key={type.value} value={type.value}>
                              {type.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Endpoint</Label>
                      <Input
                        value={editingIntegration.endpoint || ""}
                        onChange={(e) => updateEditingIntegration("endpoint", e.target.value)}
                        placeholder="https://api.example.com/v1"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>认证方式</Label>
                      <Select
                        value={editingIntegration.auth?.type || "none"}
                        onValueChange={(value) =>
                          updateEditingIntegration("auth", {
                            type: value as IntegrationAuth["type"],
                          })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {authTypes.map((type) => (
                            <SelectItem key={type.value} value={type.value}>
                              {type.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="flex gap-2 justify-end">
                      <Button onClick={handleCancel} variant="outline" size="sm">
                        <X className="h-4 w-4 mr-1" />
                        取消
                      </Button>
                      <Button onClick={handleSave} size="sm">
                        <Check className="h-4 w-4 mr-1" />
                        保存
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{integrationTypes.find((t) => t.value === integration.type)?.label}</span>
                        <span className="text-sm text-muted-foreground">{integration.endpoint}</span>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        认证: {authTypes.find((t) => t.value === (integration.auth?.type || "none"))?.label}
                      </p>
                    </div>
                    <div className="flex gap-1">
                      <Button onClick={() => handleEdit(index)} variant="ghost" size="sm">
                        <Edit2 className="h-4 w-4" />
                      </Button>
                      <Button
                        onClick={() => handleRemove(index)}
                        variant="ghost"
                        size="sm"
                        className="text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}