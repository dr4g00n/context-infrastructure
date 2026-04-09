import { useAgentCardStore } from "@/store/agentcard-store"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function ConstraintsForm() {
  const { agentCard, updateConstraints, updateTimestamp } = useAgentCardStore()

  const handleChange = (field: string, value: unknown) => {
    updateConstraints({ [field]: value })
    updateTimestamp()
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>约束配置</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="max_tokens">单次请求最大 Token</Label>
            <Input
              id="max_tokens"
              type="number"
              value={agentCard.constraints.max_tokens_per_request || ""}
              onChange={(e) => handleChange("max_tokens_per_request", parseInt(e.target.value) || undefined)}
              placeholder="4096"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="timeout">超时时间</Label>
            <Input
              id="timeout"
              value={agentCard.constraints.timeout || ""}
              onChange={(e) => handleChange("timeout", e.target.value)}
              placeholder="30s"
            />
            <p className="text-xs text-muted-foreground">例如: 30s, 1m, 5m</p>
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="rate_limit">速率限制</Label>
          <Input
            id="rate_limit"
            value={agentCard.constraints.rate_limit || ""}
            onChange={(e) => handleChange("rate_limit", e.target.value)}
            placeholder="100/min"
          />
          <p className="text-xs text-muted-foreground">格式: 次数/时间单位，如 100/min, 1000/hour</p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="max_file_size">最大文件大小</Label>
          <Input
            id="max_file_size"
            value={agentCard.constraints.max_file_size || ""}
            onChange={(e) => handleChange("max_file_size", e.target.value)}
            placeholder="10MB"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="allowed_domains">允许访问的域名</Label>
          <Input
            id="allowed_domains"
            value={agentCard.constraints.allowed_domains?.join(", ") || ""}
            onChange={(e) =>
              handleChange(
                "allowed_domains",
                e.target.value.split(",").map((s) => s.trim()).filter(Boolean)
              )
            }
            placeholder="api.example.com, *.trusted.com（用逗号分隔）"
          />
          <p className="text-xs text-muted-foreground">留空表示允许所有域名</p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="blocked_domains">禁止访问的域名</Label>
          <Input
            id="blocked_domains"
            value={agentCard.constraints.blocked_domains?.join(", ") || ""}
            onChange={(e) =>
              handleChange(
                "blocked_domains",
                e.target.value.split(",").map((s) => s.trim()).filter(Boolean)
              )
            }
            placeholder="blocked.com, *.dangerous.net（用逗号分隔）"
          />
        </div>
      </CardContent>
    </Card>
  )
}
