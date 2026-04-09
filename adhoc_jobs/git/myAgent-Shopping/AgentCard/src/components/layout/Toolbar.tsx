import { useRef, useState } from "react"
import { useAgentCardStore } from "@/store/agentcard-store"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { FilePlus, Upload, Download, FileCode } from "lucide-react"
import { exampleAgentCard } from "@/schema/defaults"
import type { AgentCard } from "@/schema/agentcard-v1"
import { AgentCardSchema } from "@/schema/agentcard-v1"

export function Toolbar() {
  const { agentCard, resetAgentCard, loadExample, setAgentCard, setValidationErrors } =
    useAgentCardStore()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [importError, setImportError] = useState<string | null>(null)
  const [showExampleDialog, setShowExampleDialog] = useState(false)

  const handleNew = () => {
    if (confirm("确定要创建新的 AgentCard 吗？未保存的更改将丢失。")) {
      resetAgentCard()
    }
  }

  const handleImportClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target?.result as string) as AgentCard
        const result = AgentCardSchema.safeParse(json)

        if (result.success) {
          setAgentCard(result.data)
          setImportError(null)
        } else {
          const errors = result.error.errors.map((err) => `${err.path.join(".")}: ${err.message}`)
          setImportError(`验证失败:\n${errors.join("\n")}`)
          setValidationErrors(errors)
        }
      } catch (err) {
        setImportError(`解析 JSON 失败: ${err instanceof Error ? err.message : String(err)}`)
      }
    }
    reader.readAsText(file)
    event.target.value = ""
  }

  const handleExport = () => {
    const jsonString = JSON.stringify(agentCard, null, 2)
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

  const handleLoadExample = () => {
    loadExample(exampleAgentCard)
    setShowExampleDialog(false)
  }

  return (
    <div className="flex items-center gap-2 p-4 border-b bg-card">
      <Button onClick={handleNew} variant="outline" size="sm" className="gap-1">
        <FilePlus className="h-4 w-4" />
        新建
      </Button>

      <Button onClick={handleImportClick} variant="outline" size="sm" className="gap-1">
        <Upload className="h-4 w-4" />
        导入
      </Button>
      <input
        ref={fileInputRef}
        type="file"
        accept=".json,application/json"
        onChange={handleFileImport}
        className="hidden"
      />

      <Button onClick={handleExport} variant="outline" size="sm" className="gap-1">
        <Download className="h-4 w-4" />
        导出
      </Button>

      <Dialog open={showExampleDialog} onOpenChange={setShowExampleDialog}>
        <DialogTrigger asChild>
          <Button variant="outline" size="sm" className="gap-1 ml-auto">
            <FileCode className="h-4 w-4" />
            加载示例
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>加载示例</DialogTitle>
            <DialogDescription>
              这将加载一个预设的代码助手示例，覆盖当前内容。
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end gap-2 mt-4">
            <Button variant="outline" onClick={() => setShowExampleDialog(false)}>
              取消
            </Button>
            <Button onClick={handleLoadExample}>确认加载</Button>
          </div>
        </DialogContent>
      </Dialog>

      {importError && (
        <Dialog open={!!importError} onOpenChange={() => setImportError(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="text-destructive">导入失败</DialogTitle>
            </DialogHeader>
            <pre className="text-sm text-destructive whitespace-pre-wrap">{importError}</pre>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}