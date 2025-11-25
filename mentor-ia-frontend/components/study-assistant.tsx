"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Send, FileText, ImageIcon, Sparkles, BookOpen, AlertCircle, Upload, Trash2, FileImage, Eye, Download } from "lucide-react"
import { askQuery, uploadDocument, listDocs, getIndexedDocuments, ocrImage } from "@/lib/api"
import type { QueryResponse, DocumentoInfo, DocumentosIndexadosResponse, OCRResponse } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

const EXAMPLE_QUERIES = [
  "¿Cuál es la historia de C y C++?",
  "Dame las técnicas principales del prompt engineering",
  "Dame algunos atajos básicos de la terminal de Linux",
]

interface Message {
  role: "user" | "assistant"
  content: string
  response?: QueryResponse
  timestamp: Date
}

export function StudyAssistant() {
  const [query, setQuery] = useState("")
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([])
  const [documents, setDocuments] = useState<DocumentoInfo[]>([])
  const [indexedDocuments, setIndexedDocuments] = useState<DocumentosIndexadosResponse | null>(null)
  const [ocrResult, setOcrResult] = useState<string>("")
  const [ocrLoading, setOcrLoading] = useState(false)
  const [activeTab, setActiveTab] = useState("context")
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const ocrFileInputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector("[data-radix-scroll-area-viewport]")
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight
      }
    }
  }, [messages, loading])

  // Load documents on mount
  useEffect(() => {
    const loadDocuments = async () => {
      try {
        const docs = await listDocs()
        setDocuments(docs)
        //console.log("Documents loaded:", docs)
      } catch (err) {
        console.error("Error loading documents:", err)
        setError("Error al cargar documentos")
      }

      try {
        const indexedResponse = await getIndexedDocuments()
        setIndexedDocuments(indexedResponse)
        //console.log("Indexed documents loaded:", indexedResponse)
      } catch (err) {
        console.error("Error loading indexed documents:", err)
        // Set empty state for indexed documents
        setIndexedDocuments({ total_chunks: 0, documentos: [], total_documentos: 0 })
      }
    }
    loadDocuments()
  }, [])

  const handleSearch = async (text: string = query) => {
    if (!text.trim()) return

    const userMessage: Message = {
      role: "user",
      content: text,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setQuery("")
    setLoading(true)
    setError(null)

    try {
      const data = await askQuery(text)
      const assistantMessage: Message = {
        role: "assistant",
        content: data.respuesta,
        response: data,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ocurrió un error inesperado")
      // Remove the user message if it failed? Or just show error.
      // Let's keep the user message but show error state.
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    setUploading(true)
    setError(null)

    try {
      const file = files[0]
      await uploadDocument(file)
      setUploadedFiles((prev) => [...prev, file.name])

      // Add a system message about the upload
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `He procesado correctamente el archivo: ${file.name}. Ahora puedes hacerme preguntas sobre su contenido.`,
          timestamp: new Date(),
        },
      ])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al subir el archivo")
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ""
    }
  }

  const clearHistory = () => {
    setMessages([])
    setError(null)
  }

  const handleOcrUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    setOcrLoading(true)
    setOcrResult("")
    setError(null)

    try {
      const file = files[0]
      console.log("Processing OCR for file:", file.name)
      const result = await ocrImage(file)
      console.log("OCR result:", result)
      setOcrResult(result.texto || "No se pudo extraer texto de la imagen")
    } catch (err) {
      console.error("OCR Error:", err)
      setError(err instanceof Error ? err.message : "Error al procesar la imagen")
    } finally {
      setOcrLoading(false)
      if (ocrFileInputRef.current) ocrFileInputRef.current.value = ""
    }
  }

  const copyOcrText = async () => {
    try {
      await navigator.clipboard.writeText(ocrResult)
      // Could add a toast notification here
      console.log("Texto copiado al portapapeles")
    } catch (err) {
      console.error("Error copiando texto:", err)
      // Fallback for older browsers
      const textArea = document.createElement("textarea")
      textArea.value = ocrResult
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
    }
  }

  const getSourceIcon = (path: string) => {
    if (path.endsWith(".png") || path.endsWith(".jpg") || path.endsWith(".jpeg")) {
      return <ImageIcon className="h-4 w-4 text-blue-500" />
    }
    return <FileText className="h-4 w-4 text-orange-500" />
  }

  const getSourceName = (path: string) => {
    return path.split("/").pop() || path
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-full overflow-hidden">
      {/* Left Column: Sidebar with Tabs */}
      <div className="lg:col-span-3 flex flex-col gap-4 h-full min-h-0">
        <Card className="border-border/50 shadow-sm flex-1 flex flex-col min-h-0">
          <CardContent className="flex-1 p-0 min-h-0">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="flex flex-col h-full">
              <div className="px-4 pt-4 pb-2 border-b border-border/50">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="context" className="text-xs">Contexto</TabsTrigger>
                  <TabsTrigger value="documents" className="text-xs">Documentos</TabsTrigger>
                  <TabsTrigger value="ocr" className="text-xs">OCR</TabsTrigger>
                </TabsList>
              </div>

              <div className="flex-1 overflow-hidden">
                {/* Context Tab */}
                <TabsContent value="context" className="h-full m-0">
                  <ScrollArea className="h-full p-4">
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <input
                          type="file"
                          ref={fileInputRef}
                          className="hidden"
                          onChange={handleFileUpload}
                          accept=".pdf,.txt,.md,.png,.jpg,.jpeg"
                        />
                        <Button
                          variant="outline"
                          className="w-full justify-start gap-2 border-dashed bg-transparent"
                          onClick={() => fileInputRef.current?.click()}
                          disabled={uploading}
                        >
                          {uploading ? (
                            <span className="animate-pulse">Subiendo...</span>
                          ) : (
                            <>
                              <Upload className="h-4 w-4" />
                              Subir Documento
                            </>
                          )}
                        </Button>
                        <p className="text-xs text-muted-foreground px-1">Soporta PDF, TXT, MD e Imágenes.</p>
                      </div>

                      {uploadedFiles.length > 0 && (
                        <div className="space-y-2">
                          <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Archivos Activos</h4>
                          <div className="space-y-1">
                            {uploadedFiles.map((file, idx) => (
                              <div
                                key={idx}
                                className="flex items-center gap-2 text-sm p-2 rounded-md bg-muted/50 border border-border/50"
                              >
                                <FileText className="h-3 w-3 text-primary" />
                                <span className="truncate flex-1">{file}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <Separator />

                      <div className="space-y-2">
                        <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Sugerencias</h4>
                        <div className="flex flex-col gap-2">
                          {EXAMPLE_QUERIES.map((q, i) => (
                            <button
                              key={i}
                              onClick={() => handleSearch(q)}
                              className="text-left text-xs p-2 rounded-md hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
                            >
                              {q}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  </ScrollArea>
                </TabsContent>

                {/* Documents Tab */}
                <TabsContent value="documents" className="h-full m-0">
                  <ScrollArea className="h-full p-4">
                    <div className="space-y-4">
                      <div className="flex items-center gap-2 mb-4">
                        <FileText className="h-4 w-4 text-primary" />
                        <h3 className="text-sm font-medium">Documentos Indexados</h3>
                      </div>

                      {indexedDocuments && indexedDocuments.documentos.length > 0 ? (
                        <div className="space-y-2">
                          {indexedDocuments.documentos.map((doc, idx) => (
                            <div
                              key={idx}
                              className="flex items-center justify-between p-3 rounded-lg border border-border/50 bg-card hover:bg-accent/50 transition-colors"
                            >
                              <div className="flex items-center gap-3 flex-1 min-w-0">
                                {getSourceIcon(doc.nombre)}
                                <div className="flex-1 min-w-0">
                                  <p className="text-sm font-medium truncate">{doc.nombre}</p>
                                  <p className="text-xs text-muted-foreground">
                                    {doc.chunks} chunks · {doc.tipo?.toUpperCase() || 'DESCONOCIDO'}
                                  </p>
                                </div>
                              </div>
                              <Button variant="ghost" size="icon" className="h-8 w-8 shrink-0">
                                <Eye className="h-4 w-4" />
                              </Button>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-8 text-muted-foreground">
                          <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
                          <p className="text-sm">No hay documentos indexados</p>
                        </div>
                      )}

                      {indexedDocuments && (
                        <div className="mt-4 p-3 bg-muted/50 rounded-lg space-y-1">
                          <p className="text-xs text-muted-foreground">
                            Documentos indexados: <span className="font-medium">{indexedDocuments.total_documentos}</span>
                          </p>
                          <p className="text-xs text-muted-foreground">
                            Total de chunks: <span className="font-medium">{indexedDocuments.total_chunks}</span>
                          </p>
                        </div>
                      )}
                    </div>
                  </ScrollArea>
                </TabsContent>

                {/* OCR Tab */}
                <TabsContent value="ocr" className="h-full m-0">
                  <ScrollArea className="h-full p-4">
                    <div className="space-y-4">
                      <div className="flex items-center gap-2 mb-4">
                        <FileImage className="h-4 w-4 text-primary" />
                        <h3 className="text-sm font-medium">OCR de Imágenes</h3>
                      </div>

                      <div className="space-y-2">
                        <input
                          type="file"
                          ref={ocrFileInputRef}
                          className="hidden"
                          onChange={handleOcrUpload}
                          accept=".png,.jpg,.jpeg"
                        />
                        <Button
                          variant="outline"
                          className="w-full justify-start gap-2 border-dashed bg-transparent"
                          onClick={() => ocrFileInputRef.current?.click()}
                          disabled={ocrLoading}
                        >
                          {ocrLoading ? (
                            <span className="animate-pulse">Procesando...</span>
                          ) : (
                            <>
                              <FileImage className="h-4 w-4" />
                              Subir Imagen
                            </>
                          )}
                        </Button>
                        <p className="text-xs text-muted-foreground px-1">Soporta PNG, JPG, JPEG.</p>
                      </div>

                      {ocrResult && (
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Texto Extraído</h4>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={copyOcrText}
                              className="h-6 px-2 text-xs"
                            >
                              Copiar
                            </Button>
                          </div>
                          <div className="p-3 bg-muted/50 rounded-lg border border-border/50">
                            <p className="text-sm whitespace-pre-wrap leading-relaxed">{ocrResult}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </ScrollArea>
                </TabsContent>
              </div>
            </Tabs>
          </CardContent>
        </Card>
      </div>

      {/* Right Column: Chat Interface */}
      <div className="lg:col-span-9 flex flex-col h-full gap-4">
        <Card className="flex-1 border-border/50 shadow-sm flex flex-col overflow-hidden">
          <CardHeader className="py-3 px-4 border-b border-border/50 bg-muted/20 flex flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-primary" />
              <span className="font-medium text-sm">Chat con Mentor IA</span>
            </div>
            {messages.length > 0 && (
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-muted-foreground hover:text-destructive"
                onClick={clearHistory}
                title="Borrar historial"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </CardHeader>

          <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
            <div className="min-h-full">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-muted-foreground p-8 opacity-50">
                <Sparkles className="h-12 w-12 mb-4" />
                <p className="text-lg font-medium">¿En qué puedo ayudarte hoy?</p>
                <p className="text-sm">Sube un archivo o haz una pregunta para comenzar.</p>
              </div>
            ) : (
              <div className="space-y-6 pb-4">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`flex flex-col gap-2 ${msg.role === "user" ? "items-end" : "items-start"}`}>
                    <div
                      className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                        msg.role === "user"
                          ? "bg-primary text-primary-foreground rounded-br-none"
                          : "bg-muted/50 border border-border/50 rounded-bl-none"
                      }`}
                    >
                      {/* Source info for assistant messages */}
                      {msg.role === "assistant" && msg.response?.fuentes && msg.response.fuentes.length > 0 && (
                        <div className="mb-2 pb-2 border-b border-border/30">
                          {msg.response.fuentes.map((source, sIdx) => (
                            <div key={sIdx} className="text-xs text-muted-foreground/80 font-mono">
                              {getSourceName(source.source_path)} · chunk {source.chunk_index || 0} score: {source.score?.toFixed(3) || '0.000'} {msg.response?.pregunta || ''}
                            </div>
                          ))}
                        </div>
                      )}
                      <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                    </div>
                  </div>
                ))}

                {loading && (
                  <div className="flex flex-col gap-2 items-start">
                    <div className="bg-muted/50 border border-border/50 rounded-2xl rounded-bl-none px-4 py-3 space-y-2 min-w-[200px]">
                      <div className="flex gap-1">
                        <span className="w-2 h-2 bg-primary/40 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                        <span className="w-2 h-2 bg-primary/40 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                        <span className="w-2 h-2 bg-primary/40 rounded-full animate-bounce"></span>
                      </div>
                    </div>
                  </div>
                )}

                {error && (
                  <Alert variant="destructive" className="max-w-[85%]">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Error</AlertTitle>
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
              </div>
            )}
            </div>
          </ScrollArea>

          <div className="p-4 bg-background border-t border-border/50">
            <div className="relative">
              <Textarea
                placeholder="Escribe tu pregunta aquí..."
                className="min-h-[60px] max-h-[180px] pr-12 resize-none py-3"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault()
                    handleSearch()
                  }
                }}
              />
              <Button
                size="icon"
                className="absolute right-2 bottom-2 h-8 w-8"
                onClick={() => handleSearch()}
                disabled={loading || !query.trim()}
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-[10px] text-muted-foreground text-center mt-2">
              El mentor puede cometer errores. Verifica la información importante.
            </p>
          </div>
        </Card>
      </div>
    </div>
  )
}