import { useAgentCardStore } from "@/store/agentcard-store"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Separator } from "@/components/ui/separator"
import type { AgentCard } from "@/schema/agentcard-v1"

const permissionGroups = [
  {
    key: "filesystem" as const,
    label: "文件系统权限",
    description: "对本地文件的操作权限",
    options: [
      { value: "read" as const, label: "读取" },
      { value: "write" as const, label: "写入" },
      { value: "delete" as const, label: "删除" },
      { value: "execute" as const, label: "执行" },
    ],
  },
  {
    key: "network" as const,
    label: "网络权限",
    description: "网络访问能力",
    options: [
      { value: "http_request" as const, label: "HTTP 请求" },
      { value: "websocket" as const, label: "WebSocket" },
      { value: "tcp" as const, label: "TCP 连接" },
      { value: "udp" as const, label: "UDP 连接" },
    ],
  },
  {
    key: "execution" as const,
    label: "执行权限",
    description: "代码执行能力",
    options: [
      { value: "bash" as const, label: "Bash 脚本" },
      { value: "python" as const, label: "Python" },
      { value: "javascript" as const, label: "JavaScript" },
      { value: "docker" as const, label: "Docker" },
      { value: "sandbox" as const, label: "沙箱环境" },
    ],
  },
  {
    key: "browser" as const,
    label: "浏览器权限",
    description: "浏览器控制能力",
    options: [
      { value: "navigation" as const, label: "页面导航" },
      { value: "screenshot" as const, label: "截图" },
      { value: "interaction" as const, label: "元素交互" },
      { value: "download" as const, label: "文件下载" },
    ],
  },
]

type PermissionGroupKey = typeof permissionGroups[number]["key"]

export function PermissionsForm() {
  const { agentCard, updatePermissions, updateTimestamp } = useAgentCardStore()

  const togglePermission = (
    group: PermissionGroupKey,
    value: string
  ) => {
    const current = agentCard.permissions[group] || []
    const updated = current.includes(value as never)
      ? current.filter((v) => v !== value)
      : [...current, value]
    updatePermissions({ [group]: updated as AgentCard["permissions"][typeof group] })
    updateTimestamp()
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>权限配置</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {permissionGroups.map((group, groupIndex) => (
          <div key={group.key}>
            {groupIndex > 0 && <Separator className="mb-6" />}
            <div className="space-y-3">
              <div>
                <Label className="text-base">{group.label}</Label>
                <p className="text-xs text-muted-foreground">{group.description}</p>
              </div>
              <div className="flex flex-wrap gap-4">
                {group.options.map((option) => (
                  <div key={option.value} className="flex items-center space-x-2">
                    <Checkbox
                      id={`${group.key}-${option.value}`}
                      checked={agentCard.permissions[group.key]?.includes(option.value as never) || false}
                      onCheckedChange={() => togglePermission(group.key, option.value)}
                    />
                    <Label
                      htmlFor={`${group.key}-${option.value}`}
                      className="text-sm font-normal"
                    >
                      {option.label}
                    </Label>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
