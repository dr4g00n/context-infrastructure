import { useAgentCardStore } from "@/store/agentcard-store"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { reasoningOptions, languageOptions } from "@/schema/defaults"

export function CapabilitiesForm() {
  const { agentCard, updateCapabilities, updateTimestamp } = useAgentCardStore()

  const handleChange = (field: string, value: unknown) => {
    updateCapabilities({ [field]: value })
    updateTimestamp()
  }

  const toggleArrayItem = (field: "reasoning" | "languages", item: string) => {
    const current = (agentCard.capabilities[field] as string[]) || []
    const updated = current.includes(item)
      ? current.filter((i) => i !== item)
      : [...current, item]
    handleChange(field, updated)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>能力配置</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Reasoning */}
        <div className="space-y-3">
          <Label>推理能力</Label>
          <div className="flex flex-wrap gap-3">
            {reasoningOptions.map((option) => (
              <div key={option.value} className="flex items-center space-x-2">
                <Checkbox
                  id={`reasoning-${option.value}`}
                  checked={agentCard.capabilities.reasoning?.includes(option.value as never) || false}
                  onCheckedChange={() => toggleArrayItem("reasoning", option.value)}
                />
                <Label htmlFor={`reasoning-${option.value}`} className="text-sm font-normal">
                  {option.label}
                </Label>
              </div>
            ))}
          </div>
        </div>

        {/* Languages */}
        <div className="space-y-3">
          <Label>支持语言</Label>
          <div className="flex flex-wrap gap-3">
            {languageOptions.map((option) => (
              <div key={option.value} className="flex items-center space-x-2">
                <Checkbox
                  id={`lang-${option.value}`}
                  checked={agentCard.capabilities.languages?.includes(option.value) || false}
                  onCheckedChange={() => toggleArrayItem("languages", option.value)}
                />
                <Label htmlFor={`lang-${option.value}`} className="text-sm font-normal">
                  {option.label}
                </Label>
              </div>
            ))}
          </div>
        </div>

        {/* Numeric inputs */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="context_window">上下文窗口</Label>
            <Input
              id="context_window"
              type="number"
              value={agentCard.capabilities.context_window || ""}
              onChange={(e) => handleChange("context_window", parseInt(e.target.value) || undefined)}
              placeholder="128000"
            />
            <p className="text-xs text-muted-foreground">最大 token 数</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="max_tokens_per_request">单次请求最大 Token</Label>
            <Input
              id="max_tokens_per_request"
              type="number"
              value={agentCard.capabilities.max_tokens_per_request || ""}
              onChange={(e) => handleChange("max_tokens_per_request", parseInt(e.target.value) || undefined)}
              placeholder="4096"
            />
          </div>
        </div>

        {/* Boolean options */}
        <div className="flex flex-wrap gap-6">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="supports_vision"
              checked={agentCard.capabilities.supports_vision}
              onCheckedChange={(checked: boolean) => handleChange("supports_vision", checked)}
            />
            <Label htmlFor="supports_vision" className="text-sm font-normal">
              支持视觉
            </Label>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="supports_audio"
              checked={agentCard.capabilities.supports_audio}
              onCheckedChange={(checked: boolean) => handleChange("supports_audio", checked)}
            />
            <Label htmlFor="supports_audio" className="text-sm font-normal">
              支持音频
            </Label>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="supports_streaming"
              checked={agentCard.capabilities.supports_streaming}
              onCheckedChange={(checked: boolean) => handleChange("supports_streaming", checked)}
            />
            <Label htmlFor="supports_streaming" className="text-sm font-normal">
              支持流式输出
            </Label>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
