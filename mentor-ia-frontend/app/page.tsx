// import Image from "next/image";

// export default function Home() {
//   return (
//     <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
//       <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-between py-32 px-16 bg-white dark:bg-black sm:items-start">
//         <Image
//           className="dark:invert"
//           src="/next.svg"
//           alt="Next.js logo"
//           width={100}
//           height={20}
//           priority
//         />
//         <div className="flex flex-col items-center gap-6 text-center sm:items-start sm:text-left">
//           <h1 className="max-w-xs text-3xl font-semibold leading-10 tracking-tight text-black dark:text-zinc-50">
//             To get started, edit the page.tsx file.
//           </h1>
//           <p className="max-w-md text-lg leading-8 text-zinc-600 dark:text-zinc-400">
//             Looking for a starting point or more instructions? Head over to{" "}
//             <a
//               href="https://vercel.com/templates?framework=next.js&utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
//               className="font-medium text-zinc-950 dark:text-zinc-50"
//             >
//               Templates
//             </a>{" "}
//             or the{" "}
//             <a
//               href="https://nextjs.org/learn?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
//               className="font-medium text-zinc-950 dark:text-zinc-50"
//             >
//               Learning
//             </a>{" "}
//             center.
//           </p>
//         </div>
//         <div className="flex flex-col gap-4 text-base font-medium sm:flex-row">
//           <a
//             className="flex h-12 w-full items-center justify-center gap-2 rounded-full bg-foreground px-5 text-background transition-colors hover:bg-[#383838] dark:hover:bg-[#ccc] md:w-[158px]"
//             href="https://vercel.com/new?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
//             target="_blank"
//             rel="noopener noreferrer"
//           >
//             <Image
//               className="dark:invert"
//               src="/vercel.svg"
//               alt="Vercel logomark"
//               width={16}
//               height={16}
//             />
//             Deploy Now
//           </a>
//           <a
//             className="flex h-12 w-full items-center justify-center rounded-full border border-solid border-black/[.08] px-5 transition-colors hover:border-transparent hover:bg-black/[.04] dark:border-white/[.145] dark:hover:bg-[#1a1a1a] md:w-[158px]"
//             href="https://nextjs.org/docs?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
//             target="_blank"
//             rel="noopener noreferrer"
//           >
//             Documentation
//           </a>
//         </div>
//       </main>
//     </div>
//   );
// }

// app/page.tsx
"use client";

import { useState } from "react";
import { QueryBox } from "@/components/QueryBox";
import { AnswerCard } from "@/components/AnswerCard";
import { SourcesList } from "@/components/SourcesList";
import { askQuery } from "@/lib/api";
import { Fuente, QueryResponse } from "@/lib/types";

import { PlanSection } from "@/components/PlanSection"; //nuevo

export default function HomePage() {
  const [loading, setLoading] = useState(false);
  const [pregunta, setPregunta] = useState<string | undefined>(undefined);
  const [respuesta, setRespuesta] = useState<string | undefined>(undefined);
  const [origen, setOrigen] = useState<string | undefined>(undefined);
  const [detalle, setDetalle] = useState<string | undefined>(undefined);
  const [fuentes, setFuentes] = useState<Fuente[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function handleAsk(p: string) {
    setLoading(true);
    setError(null);
    setRespuesta(undefined);
    setFuentes([]);

    try {
      const res: QueryResponse = await askQuery(p);
      setPregunta(res.pregunta);
      setRespuesta(res.respuesta);
      setOrigen(res.origen);
      setDetalle(res.detalle_origen);
      setFuentes(res.fuentes || []);
    } catch (e: any) {
      console.error(e);
      setError(e?.message || "Error al consultar el backend");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-10">
      <section className="space-y-4">
        <h1 className="text-2xl font-semibold tracking-tight">
          Asistente de estudio con RAG
        </h1>
        <p className="max-w-2xl text-sm text-neutral-400">
          Este frontend consulta tu backend FastAPI con Qdrant y Gemini. Puedes
          hacer preguntas sobre tus PDFs y sobre imágenes que hayan pasado por
          OCR. El sistema te mostrará también los fragmentos usados como
          contexto.
        </p>
      </section>

      <section className="space-y-4">
        <QueryBox onSubmit={handleAsk} loading={loading} />

        {error && (
          <p className="mt-4 w-full max-w-2xl mx-auto text-xs text-red-400 bg-red-950/40 border border-red-900/60 rounded-xl px-3 py-2">
            {error}
          </p>
        )}

        <AnswerCard
          pregunta={pregunta}
          respuesta={respuesta}
          origen={origen}
          detalle_origen={detalle}
        />

        <SourcesList fuentes={fuentes} />
        {/* nuevo */}
        <PlanSection /> 
      </section>
    </div>
  );
}
