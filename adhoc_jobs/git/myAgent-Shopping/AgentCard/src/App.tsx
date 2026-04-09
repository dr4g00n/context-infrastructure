import { Toolbar } from "@/components/layout/Toolbar"
import { BasicInfoForm } from "@/components/form/BasicInfoForm"
import { CapabilitiesForm } from "@/components/form/CapabilitiesForm"
import { ToolsForm } from "@/components/form/ToolsForm"
import { PermissionsForm } from "@/components/form/PermissionsForm"
import { ConstraintsForm } from "@/components/form/ConstraintsForm"
import { IntegrationsForm } from "@/components/form/IntegrationsForm"
import { MetadataForm } from "@/components/form/MetadataForm"
import { JsonPreview } from "@/components/preview/JsonPreview"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { Separator } from "@/components/ui/separator"

function App() {
  return (
    <div className="min-h-screen bg-background">
      <Toolbar />
      <div className="flex h-[calc(100vh-65px)]">
        {/* Left panel - Forms */}
        <div className="w-1/2 overflow-y-auto border-r">
          <div className="p-6 space-y-6">
            <Accordion type="multiple" defaultValue={["basic"]} className="space-y-4">
              <AccordionItem value="basic" className="border-0">
                <AccordionTrigger className="text-lg font-semibold hover:no-underline">
                  基础信息
                </AccordionTrigger>
                <AccordionContent>
                  <BasicInfoForm />
                </AccordionContent>
              </AccordionItem>
              <Separator />
              <AccordionItem value="capabilities" className="border-0">
                <AccordionTrigger className="text-lg font-semibold hover:no-underline">
                  能力配置
                </AccordionTrigger>
                <AccordionContent>
                  <CapabilitiesForm />
                </AccordionContent>
              </AccordionItem>
              <Separator />
              <AccordionItem value="tools" className="border-0">
                <AccordionTrigger className="text-lg font-semibold hover:no-underline">
                  工具配置
                </AccordionTrigger>
                <AccordionContent>
                  <ToolsForm />
                </AccordionContent>
              </AccordionItem>
              <Separator />
              <AccordionItem value="permissions" className="border-0">
                <AccordionTrigger className="text-lg font-semibold hover:no-underline">
                  权限配置
                </AccordionTrigger>
                <AccordionContent>
                  <PermissionsForm />
                </AccordionContent>
              </AccordionItem>
              <Separator />
              <AccordionItem value="constraints" className="border-0">
                <AccordionTrigger className="text-lg font-semibold hover:no-underline">
                  约束配置
                </AccordionTrigger>
                <AccordionContent>
                  <ConstraintsForm />
                </AccordionContent>
              </AccordionItem>
              <Separator />
              <AccordionItem value="integrations" className="border-0">
                <AccordionTrigger className="text-lg font-semibold hover:no-underline">
                  集成配置
                </AccordionTrigger>
                <AccordionContent>
                  <IntegrationsForm />
                </AccordionContent>
              </AccordionItem>
              <Separator />
              <AccordionItem value="metadata" className="border-0">
                <AccordionTrigger className="text-lg font-semibold hover:no-underline">
                  元数据
                </AccordionTrigger>
                <AccordionContent>
                  <MetadataForm />
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
        </div>
        {/* Right panel - Preview */}
        <div className="w-1/2 p-6 bg-muted/30">
          <JsonPreview />
        </div>
      </div>
    </div>
  )
}

export default App