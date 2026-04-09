import { useAgentCardStore } from "@/store/agentcard-store"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { categoryOptions } from "@/schema/defaults"

export function MetadataForm() {
  const { agentCard, updateMetadata, updateTimestamp } = useAgentCardStore()

  const handleChange = (field: string, value: unknown) => {
    updateMetadata({ [field]: value })
    updateTimestamp()
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>元数据</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="category">类别</Label>
          <Select
            value={agentCard.metadata.category}
            onValueChange={(value) => handleChange("category", value)}
          >
            <SelectTrigger id="category">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {categoryOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="tags">标签</Label>
          <Input
            id="tags"
            value={agentCard.metadata.tags?.join(", ") || ""}
            onChange={(e) =>
              handleChange(
                "tags",
                e.target.value.split(",").map((s) => s.trim()).filter(Boolean)
              )
            }
            placeholder="assistant, coding, developer-tools（用逗号分隔）"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="license">许可证</Label>
          <Input
            id="license"
            value={agentCard.metadata.license || ""}
            onChange={(e) => handleChange("license", e.target.value)}
            placeholder="MIT"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="homepage">主页</Label>
          <Input
            id="homepage"
            value={agentCard.metadata.homepage || ""}
            onChange={(e) => handleChange("homepage", e.target.value)}
            placeholder="https://example.com/agent"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="repository">代码仓库</Label>
          <Input
            id="repository"
            value={agentCard.metadata.repository || ""}
            onChange={(e) => handleChange("repository", e.target.value)}
            placeholder="https://github.com/example/agent"
          />
        </div>
      </CardContent>
    </Card>
  )
}
