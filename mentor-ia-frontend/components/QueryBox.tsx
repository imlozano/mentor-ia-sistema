// components/QueryBox.tsx
"use client";

import { FormEvent, useState } from "react";

interface QueryBoxProps {
  onSubmit: (pregunta: string) => Promise<void> | void;
  loading?: boolean;
}

export function QueryBox({ onSubmit, loading }: QueryBoxProps) {
  const [value, setValue] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!value.trim() || loading) return;
    await onSubmit(value.trim());
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="w-full max-w-2xl mx-auto flex flex-col gap-3"
    >
      <label className="text-sm font-medium text-neutral-300">
        Haz una pregunta a tu Mentor IA
      </label>

      <textarea
        className="w-full min-h-[120px] rounded-2xl border border-neutral-800 bg-neutral-950/70 px-4 py-3 text-sm text-neutral-100 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition"
        placeholder="Ejemplo: “Cuéntame la historia de C y C++”"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />

      <div className="flex items-center gap-3 justify-between">
        <p className="text-xs text-neutral-500">
          El sistema usará tus PDFs e imágenes (OCR) para responder.
        </p>
        <button
          type="submit"
          disabled={loading || !value.trim()}
          className="inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium 
          bg-indigo-500 hover:bg-indigo-400 disabled:bg-neutral-800 disabled:text-neutral-500 
          text-white transition"
        >
          {loading ? "Consultando..." : "Preguntar"}
        </button>
      </div>
    </form>
  );
}
