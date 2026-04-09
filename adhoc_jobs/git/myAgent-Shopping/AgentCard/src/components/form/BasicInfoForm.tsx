import { useAgentCardStore } from "@/store/agentcard-store"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function BasicInfoForm() {
  const { agentCard, updateAgentCard, updateTimestamp } = useAgentCardStore()

  const handleChange = (field: string, value: string) => {
    updateAgentCard({ [field]: value })
    updateTimestamp()
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>基础信息</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="id">Agent ID</Label>
          <Input
            id="id"
            value={agentCard.id}
            onChange={(e) => handleChange("id", e.target.value)}
            placeholder="唯一标识符"
          />
          <p className="text-xs text-muted-foreground">Agent 的唯一标识符，建议使用小写字母和连字符</p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="name">名称</Label>
          <Input
            id="name"
            value={agentCard.name}
            onChange={(e) => handleChange("name", e.target.value)}
            placeholder="Agent 名称"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="version">版本</Label>
          <Input
            id="version"
            value={agentCard.version}
            onChange={(e) => handleChange("version", e.target.value)}
            placeholder="1.0.0"
          />
          <p className="text-xs text-muted-foreground">语义化版本号格式：x.y.z</p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="description">描述</Label>
          <Textarea
            id="description"
            value={agentCard.description}
            onChange={(e) => handleChange("description", e.target.value)}
            placeholder="描述这个 Agent 的主要功能和用途"
            rows={3}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="author">作者</Label>
          <Input
            id="author"
            value={agentCard.author || ""}
            onChange={(e) => handleChange("author", e.target.value)}
            placeholder="作者或团队名称"
          />
        </div>
      </CardContent>
    </Card>
  )
}
