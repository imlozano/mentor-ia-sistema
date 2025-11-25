import { Brain } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { StudyAssistant } from "@/components/study-assistant"
import { ReviewPlan } from "@/components/review-plan"

export default function Home() {
  return (
    <div className="min-h-screen w-full bg-background selection:bg-primary/10 selection:text-primary">
      {/* Header */}
      <header className="w-full border-b border-border/40 bg-background">
        <div className="px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-primary/10 p-2.5 rounded-xl">
              <Brain className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-foreground">Mentor IA</h1>
              <p className="text-sm text-muted-foreground hidden sm:block leading-tight">
                Asistente inteligente de aprendizaje
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-sm font-medium text-muted-foreground">Online</span>
          </div>
        </div>
      </header>

      {/* Main Content - Full Screen */}
      <main className="w-full min-h-[calc(100vh-4rem)] bg-background">
        <Tabs defaultValue="assistant" className="w-full h-full flex flex-col">
          {/* Tab Navigation */}
          <div className="w-full px-6 lg:px-8 py-6 border-b border-border/40 bg-background">
            <div className="flex items-center justify-center">
              <TabsList className="grid w-full max-w-lg grid-cols-2 p-1.5 bg-muted/50 rounded-xl">
                <TabsTrigger
                  value="assistant"
                  className="data-[state=active]:bg-background data-[state=active]:shadow-sm text-sm font-medium rounded-lg transition-all"
                >
                  Asistente de Estudio
                </TabsTrigger>
                <TabsTrigger
                  value="plan"
                  className="data-[state=active]:bg-background data-[state=active]:shadow-sm text-sm font-medium rounded-lg transition-all"
                >
                  Plan de Repaso
                </TabsTrigger>
              </TabsList>
            </div>
          </div>

          {/* Tab Content - Full Height */}
          <div className="flex-1 w-full overflow-hidden">
            <TabsContent value="assistant" className="w-full h-full m-0 outline-none data-[state=active]:animate-in data-[state=active]:fade-in-0 data-[state=active]:duration-300">
              <div className="w-full h-full px-6 lg:px-8 py-6">
                <StudyAssistant />
              </div>
            </TabsContent>

            <TabsContent value="plan" className="w-full h-full m-0 outline-none data-[state=active]:animate-in data-[state=active]:fade-in-0 data-[state=active]:duration-300">
              <div className="w-full h-full px-6 lg:px-8 py-6">
                <ReviewPlan />
              </div>
            </TabsContent>
          </div>
        </Tabs>
      </main>
    </div>
  )
}
