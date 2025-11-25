"use client"

import type React from "react"
import { useState, useRef } from "react"
import { CalendarIcon, BookOpen, Clock, CheckCircle2, ArrowRight, AlertCircle, Upload } from "lucide-react"
import { createPlan, uploadDocument } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"

import type { PlanRepasoResponse } from "@/lib/types"

export function ReviewPlan() {
  const [mode, setMode] = useState<"topic" | "file">("topic")
  const [topic, setTopic] = useState("")
  const [startDate, setStartDate] = useState("")
  const [email, setEmail] = useState("")
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [plan, setPlan] = useState<PlanRepasoResponse | null>(null)
  const [uploadedFile, setUploadedFile] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Helper function to render description
  const renderDescription = (desc: string | import("@/lib/types").SesionDescripcionBlock[]) => {
    if (typeof desc === "string") {
      return <p className="text-sm leading-relaxed whitespace-pre-wrap text-foreground/90">{desc}</p>
    }

    // If it's an array of blocks
    return desc.map((block, i) => (
      <div key={i} className="space-y-2">
        <p className="text-sm leading-relaxed whitespace-pre-wrap text-foreground/90">{block.text}</p>
        {block.extras && (
          <pre className="text-[10px] bg-muted/50 p-2 rounded text-muted-foreground overflow-x-auto">
            {JSON.stringify(block.extras, null, 2)}
          </pre>
        )}
      </div>
    ))
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    setUploading(true)
    setError(null)

    try {
      const file = files[0]
      await uploadDocument(file)
      setUploadedFile(file.name)
      setTopic(`Plan basado en: ${file.name}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al subir el archivo")
    } finally {
      setUploading(false)
    }
  }

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!topic.trim() && !uploadedFile) return

    setLoading(true)
    setError(null)

    try {
      const data = await createPlan(topic, startDate || undefined, email || undefined)
      setPlan(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ocurrió un error al generar el plan")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 h-full overflow-hidden">
      {/* Left Column: Configuration */}
      <div className="lg:col-span-4 space-y-6">
        <Card className="border-border/50 shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CalendarIcon className="h-5 w-5 text-primary" />
              Configurar Plan
            </CardTitle>
            <CardDescription>Genera un cronograma de repaso espaciado.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleGenerate} className="space-y-6">
              <div className="space-y-3">
                <Label>Fuente del Plan</Label>
                <RadioGroup
                  defaultValue="topic"
                  value={mode}
                  onValueChange={(v) => setMode(v as "topic" | "file")}
                  className="grid grid-cols-2 gap-4"
                >
                  <div>
                    <RadioGroupItem value="topic" id="mode-topic" className="peer sr-only" />
                    <Label
                      htmlFor="mode-topic"
                      className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                    >
                      <BookOpen className="mb-2 h-6 w-6" />
                      Tema
                    </Label>
                  </div>
                  <div>
                    <RadioGroupItem value="file" id="mode-file" className="peer sr-only" />
                    <Label
                      htmlFor="mode-file"
                      className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                    >
                      <Upload className="mb-2 h-6 w-6" />
                      Archivo
                    </Label>
                  </div>
                </RadioGroup>
              </div>

              {mode === "topic" ? (
                <div className="space-y-2 animate-in fade-in zoom-in-95 duration-200">
                  <Label htmlFor="topic">Tema de estudio</Label>
                  <Input
                    id="topic"
                    placeholder="Ej: Algoritmos de ordenamiento"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    required
                  />
                </div>
              ) : (
                <div className="space-y-2 animate-in fade-in zoom-in-95 duration-200">
                  <Label>Subir Material</Label>
                  <input
                    type="file"
                    ref={fileInputRef}
                    className="hidden"
                    onChange={handleFileUpload}
                    accept=".pdf,.txt,.md"
                  />
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      className="w-full border-dashed bg-transparent"
                      onClick={() => fileInputRef.current?.click()}
                      disabled={uploading}
                    >
                      {uploading ? "Subiendo..." : "Seleccionar PDF/TXT"}
                    </Button>
                  </div>
                  {uploadedFile && (
                    <div className="flex items-center gap-2 text-sm text-green-600 bg-green-50 p-2 rounded border border-green-100">
                      <CheckCircle2 className="h-4 w-4" />
                      <span className="truncate">{uploadedFile}</span>
                    </div>
                  )}
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="date">Fecha de inicio (Opcional)</Label>
                <Input
                  id="date"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="block w-full"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email para envío automático (Opcional)</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="tu-email@ejemplo.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                <p className="text-xs text-muted-foreground">
                  Si proporcionas un email, el plan se enviará automáticamente por Make.com
                </p>
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={loading || (mode === "topic" && !topic.trim()) || (mode === "file" && !uploadedFile)}
              >
                {loading ? "Generando Plan..." : "Generar Plan de Repaso"}
                {!loading && <ArrowRight className="ml-2 h-4 w-4" />}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="bg-muted/30 rounded-lg p-4 border border-border/50 text-sm text-muted-foreground">
          <h4 className="font-medium text-foreground mb-2 flex items-center gap-2">
            <Clock className="h-4 w-4" />
            ¿Cómo funciona?
          </h4>
          <p>
            Este sistema utiliza la técnica de <strong>Repaso Espaciado</strong>. Generaremos sesiones de estudio
            distribuidas en el tiempo (ej: mañana, en una semana, en un mes) para optimizar tu retención a largo plazo.
          </p>
        </div>
      </div>

      {/* Right Column: Plan Display */}
      <div className="lg:col-span-8">
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {loading && (
          <div className="space-y-4">
            <Skeleton className="h-32 w-full rounded-xl" />
            <div className="space-y-4 mt-8">
              {[1, 2, 3, 4].map((i) => (
                <Skeleton key={i} className="h-24 w-full rounded-lg" />
              ))}
            </div>
          </div>
        )}

        {!loading && plan && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Summary Card */}
            <Card className="bg-primary/5 border-primary/20 shadow-sm">
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                  <div>
                    <h2 className="text-2xl font-bold tracking-tight">{plan.tema}</h2>
                    <p className="text-muted-foreground flex items-center gap-2 mt-1">
                      <CalendarIcon className="h-4 w-4" />
                      Inicio: {new Date(plan.fecha_inicio).toLocaleDateString()}
                    </p>
                  </div>
                  <Badge
                    variant="secondary"
                    className="self-start md:self-center px-3 py-1"
                  >
                    Plan Generado
                  </Badge>
                </div>
              </CardContent>
            </Card>

            {/* Timeline */}
            <div className="relative space-y-0">
              <div className="absolute left-4 top-4 bottom-4 w-0.5 bg-border/50 hidden md:block" />

              <div className="space-y-6">
                {plan.sesiones.map((session, idx) => (
                  <div key={idx} className="relative md:pl-12 group">
                    {/* Timeline Dot */}
                    <div className="absolute left-[11px] top-6 w-2.5 h-2.5 rounded-full bg-primary ring-4 ring-background hidden md:block group-hover:scale-125 transition-transform" />

                    <Card className="border-border/50 hover:border-primary/30 transition-colors shadow-sm">
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <Badge variant="outline" className="font-mono font-bold bg-muted/50">
                              {session.tipo}
                            </Badge>
                            <span className="text-sm font-medium text-muted-foreground">
                              {new Date(session.fecha).toLocaleDateString(undefined, {
                                weekday: "long",
                                year: "numeric",
                                month: "long",
                                day: "numeric",
                              })}
                            </span>
                          </div>
                          <CheckCircle2 className="h-5 w-5 text-muted-foreground/20" />
                        </div>
                      </CardHeader>
                      <CardContent>
                        {renderDescription(session.descripcion)}
                      </CardContent>
                    </Card>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {!loading && !plan && !error && (
          <div className="h-full flex flex-col items-center justify-center text-muted-foreground p-12 border-2 border-dashed border-border/50 rounded-xl bg-muted/10">
            <BookOpen className="h-12 w-12 mb-4 opacity-20" />
            <p className="text-lg font-medium">Planifica tu éxito</p>
            <p className="text-sm">
              Configura un tema o sube un archivo para generar tu cronograma de estudio personalizado.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}