// app/ocr/page.tsx
import { OCRUploader } from "@/components/OCRUploader";

export default function OCRPage() {
  return (
    <div className="space-y-8">
      <section className="space-y-4">
        <h1 className="text-2xl font-semibold tracking-tight">
          OCR de imágenes con Google Vision
        </h1>
        <p className="max-w-2xl text-sm text-neutral-400">
          Sube una imagen con texto (apuntes, capturas, material de clase) y el
          sistema extraerá el contenido usando tu backend FastAPI + Google Cloud
          Vision. Este módulo es independiente del RAG, pero está alineado con
          el flujo de tu proyecto.
        </p>
      </section>

      <section>
        <OCRUploader />
      </section>
    </div>
  );
}
