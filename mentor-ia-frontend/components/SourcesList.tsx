// components/SourcesList.tsx
import { Fuente } from "@/lib/types";

interface SourcesListProps {
  fuentes: Fuente[];
}

export function SourcesList({ fuentes }: SourcesListProps) {
  if (!fuentes || fuentes.length === 0) return null;

  return (
    <div className="w-full max-w-3xl mx-auto mt-6">
      <h3 className="text-xs uppercase tracking-wide text-neutral-500 mb-3">
        Fragmentos usados como contexto
      </h3>

      <div className="space-y-3">
        {fuentes.slice(0, 5).map((f, idx) => (
          <div
            key={`${f.source_path}-${f.chunk_index}-${idx}`}
            className="rounded-2xl border border-neutral-800 bg-neutral-950/70 px-4 py-3 text-xs text-neutral-200"
          >
            <div className="flex items-center justify-between mb-2 text-[11px] text-neutral-500">
              <span className="truncate">
                {f.source_path.split("/").slice(-1)[0]} · chunk{" "}
                {f.chunk_index ?? "-"}
              </span>
              <span className="text-[10px] bg-neutral-900/70 px-2 py-0.5 rounded-full">
                score: {f.score?.toFixed(3) ?? "–"}
              </span>
            </div>
            <p className="line-clamp-4 whitespace-pre-wrap">{f.texto}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
