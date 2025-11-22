// components/OCRUploader.tsx
"use client";

import { useState } from "react";
import { ocrImage } from "@/lib/api";
import { OCRResponse } from "@/lib/types";

export function OCRUploader() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [texto, setTexto] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleUpload() {
    if (!file || loading) return;
    setLoading(true);
    setError(null);
    setTexto(null);

    // try { #<-- Código anterior con formdata
    //   const formData = new FormData();
    //   formData.append("file", file);

    // //   const res: OCRResponse = await ocrImage(formData);
    //   const res: OCRResponse = await ocrImage(file); // Usando la función corregida
    //   setTexto(res.texto || "(No se detectó texto)");
    // } catch (e: any) {
    //   setError(e?.message || "Error procesando la imagen");
    // } finally {
    //   setLoading(false);
    // }

    try { // <- Código corregido
        const res: OCRResponse = await ocrImage(file);
        setTexto(res.texto || "(No se detectó texto)");
    } catch (e: any) {
        setError(e?.message || "Error procesando la imagen");
    } finally {
        setLoading(false);
    }

  }

  return (
    <div className="w-full max-w-2xl mx-auto space-y-4">
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-300">
          Sube una imagen con texto
        </label>
        <div className="flex flex-col gap-3 rounded-2xl border border-dashed border-neutral-800 bg-neutral-950/60 px-4 py-4">
          <input
            type="file"
            accept="image/png,image/jpeg,image/jpg"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="text-xs text-neutral-400 file:mr-3 file:rounded-full file:border-0 file:bg-neutral-800 file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-neutral-100 hover:file:bg-neutral-700"
          />
          <div className="flex items-center justify-between text-xs text-neutral-500">
            <span>
              Formatos soportados: PNG, JPG. Usa imágenes similares a tus
              apuntes o capturas de pantalla.
            </span>
            <button
              type="button"
              onClick={handleUpload}
              disabled={!file || loading}
              className="rounded-full px-4 py-1.5 text-xs font-medium 
              bg-indigo-500 hover:bg-indigo-400 disabled:bg-neutral-800 
              disabled:text-neutral-500 text-white transition"
            >
              {loading ? "Analizando..." : "Extraer texto"}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <p className="text-xs text-red-400 bg-red-950/40 border border-red-900/60 rounded-xl px-3 py-2">
          {error}
        </p>
      )}

      {texto && (
        <div className="space-y-2">
          <h3 className="text-xs uppercase tracking-wide text-neutral-500">
            Texto extraído
          </h3>
          <div className="rounded-2xl border border-neutral-800 bg-neutral-900/70 px-4 py-3 text-sm text-neutral-100 whitespace-pre-wrap">
            {texto}
          </div>
        </div>
      )}
    </div>
  );
}
