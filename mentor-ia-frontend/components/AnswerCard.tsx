// components/AnswerCard.tsx

interface AnswerCardProps {
  pregunta?: string;
  respuesta?: string;
  origen?: string;
  detalle_origen?: string;
}

export function AnswerCard({
  pregunta,
  respuesta,
  origen,
  detalle_origen,
}: AnswerCardProps) {
  if (!respuesta) return null;

  return (
    <div className="w-full max-w-3xl mx-auto mt-8 space-y-4">
      {pregunta && (
        <div className="text-xs uppercase tracking-wide text-indigo-400">
          Pregunta
        </div>
      )}
      {pregunta && (
        <div className="rounded-2xl border border-neutral-800 bg-neutral-950/60 px-4 py-3 text-sm text-neutral-200">
          {pregunta}
        </div>
      )}

      <div className="flex items-center justify-between text-xs text-neutral-500">
        <span>Respuesta del Mentor IA</span>
        {origen && (
          <span className="inline-flex items-center gap-2">
            <span
              className={`h-2 w-2 rounded-full ${
                origen === "rag" ? "bg-emerald-500" : "bg-sky-500"
              }`}
            />
            <span className="capitalize">
              {origen === "rag" ? "RAG (con PDFs/imágenes)" : origen}
            </span>
          </span>
        )}
      </div>

      <div className="rounded-2xl border border-neutral-800 bg-neutral-900/70 px-5 py-4 text-sm leading-relaxed text-neutral-100 whitespace-pre-wrap">
        {respuesta}
      </div>

      {detalle_origen && (
        <p className="text-xs text-neutral-500">{detalle_origen}</p>
      )}
    </div>
  );
}
