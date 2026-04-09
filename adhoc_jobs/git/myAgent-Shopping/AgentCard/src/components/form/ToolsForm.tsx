import { useState } from "react"
import { useAgentCardStore } from "@/store/agentcard-store"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Plus, Trash2, Edit2, Check, X } from "lucide-react"
import type { Tool } from "@/schema/agentcard-v1"
import { defaultTool } from "@/schema/defaults"

export function ToolsForm() {
  const { agentCard, addTool, updateTool, removeTool, updateTimestamp } = useAgentCardStore()
  const [editingIndex, setEditingIndex] = useState<number | null>(null)
  const [editingTool, setEditingTool] = useState<Tool>(defaultTool())

  const handleAdd = () => {
    addTool(defaultTool())
    setEditingIndex(agentCard.tools.length)
    setEditingTool(defaultTool())
    updateTimestamp()
  }

  const handleEdit = (index: number) => {
    setEditingIndex(index)
    setEditingTool({ ...agentCard.tools[index] })
  }

  const handleSave = () => {
    if (editingIndex !== null) {
      updateTool(editingIndex, editingTool)
      setEditingIndex(null)
      updateTimestamp()
    }
  }

  const handleCancel = () => {
    setEditingIndex(null)
    setEditingTool(defaultTool())
  }

  const handleRemove = (index: number) => {
    removeTool(index)
    if (editingIndex === index) {
      setEditingIndex(null)
    }
    updateTimestamp()
  }

  const updateEditingTool = (field: keyof Tool, value: unknown) => {
    setEditingTool((prev) => ({ ...prev, [field]: value }))
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>工具配置</CardTitle>
        <Button onClick={handleAdd} size="sm" className="gap-1">
          <Plus className="h-4 w-4" />
          添加工具
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        {agentCard.tools.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">
            暂无工具，点击上方按钮添加
          </p>
        ) : (
          <div className="space-y-3">
            {agentCard.tools.map((tool, index) => (
              <div key={index} className="border rounded-lg p-4">
                {editingIndex === index ? (
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label>工具名称</Label>
                      <Input
                        value={editingTool.name}
                        onChange={(e) => updateEditingTool("name", e.target.value)}
                        placeholder="tool_name"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>描述</Label>
                      <Textarea
                        value={editingTool.description}
                        onChange={(e) => updateEditingTool("description", e.target.value)}
                        placeholder="工具功能描述"
                        rows={2}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>所需权限</Label>
                      <Input
                        value={editingTool.required_permissions?.join(", ") || ""}
                        onChange={(e) =>
                          updateEditingTool(
                            "required_permissions",
                            e.target.value.split(",").map((s) => s.trim()).filter(Boolean)
                          )
                        }
                        placeholder="read, write, execute（用逗号分隔）"
                      />
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
                        <span className="font-medium">{tool.name}</span>
                        {tool.required_permissions && tool.required_permissions.length > 0 && (
                          <div className="flex gap-1">
                            {tool.required_permissions.map((perm) => (
                              <Badge key={perm} variant="secondary" className="text-xs">
                                {perm}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">{tool.description}</p>
                    </div>
                    <div className="flex gap-1">
                      <Button
                        onClick={() => handleEdit(index)}
                        variant="ghost"
                        size="sm"
                      >
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
