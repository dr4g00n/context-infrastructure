import { useEffect, useRef } from "react"
import { useAgentCardStore } from "@/store/agentcard-store"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { AgentCardSchema } from "@/schema/agentcard-v1"
import Prism from "prismjs"
import "prismjs/components/prism-json"
import "prismjs/themes/prism-tomorrow.css"
import { Check, X } from "lucide-react"

export function JsonPreview() {
  const { agentCard, validationErrors, setValidationErrors } = useAgentCardStore()
  const codeRef = useRef<HTMLElement>(null)

  const jsonString = JSON.stringify(agentCard, null, 2)

  useEffect(() => {
    // 验证 JSON
    const result = AgentCardSchema.safeParse(agentCard)
    if (!result.success) {
      const errors = result.error.errors.map((e) => `${e.path.join(".")}: ${e.message}`)
      setValidationErrors(errors)
    } else {
      setValidationErrors([])
    }
  }, [agentCard, setValidationErrors])

  useEffect(() => {
    if (codeRef.current) {
      Prism.highlightElement(codeRef.current)
    }
  }, [jsonString])

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString)
  }

  const handleDownload = () => {
    const blob = new Blob([jsonString], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `${agentCard.id || "agentcard"}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="flex items-center gap-2">
          <CardTitle className="text-base">JSON 预览</CardTitle>
          {validationErrors.length === 0 ? (
            <Badge variant="default" className="gap-1 bg-green-600">
              <Check className="h-3 w-3" />
              有效
            </Badge>
          ) : (
            <Badge variant="destructive" className="gap-1">
              <X className="h-3 w-3" />
              {validationErrors.length} 个错误
            </Badge>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleCopy}
            className="text-xs px-3 py-1.5 rounded bg-secondary hover:bg-secondary/80 transition-colors"
          >
            复制
          </button>
          <button
            onClick={handleDownload}
            className="text-xs px-3 py-1.5 rounded bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            下载
          </button>
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-auto p-0">
        {validationErrors.length > 0 && (
          <div className="px-4 py-2 bg-destructive/10 border-b border-destructive/20">
            <ul className="text-xs text-destructive space-y-1">
              {validationErrors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          </div>
        )}
        <pre className="p-4 text-sm overflow-auto h-full" style={{ margin: 0 }}>
          <code ref={codeRef} className="language-json">
            {jsonString}
          </code>
        </pre>
      </CardContent>
    </Card>
  )
}
