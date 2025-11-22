// "use client";

// import { useState } from "react";
// import { createPlan } from "@/lib/api";
// import type { PlanRepasoResponse, BloqueRepaso } from "@/lib/types";

// export function PlanSection() {
//   const [tema, setTema] = useState("");
//   const [fechaInicio, setFechaInicio] = useState("");
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState<string | null>(null);
//   const [plan, setPlan] = useState<PlanRepasoResponse | null>(null);

//   async function handleGenerate(e: React.FormEvent) {
//     e.preventDefault();
//     if (!tema || loading) return;

//     setLoading(true);
//     setError(null);
//     setPlan(null);

//     try {
//       const resp = await createPlan(tema, fechaInicio || undefined);
//       setPlan(resp);
//     } catch (e: any) {
//       console.error(e);
//       setError(e?.message ?? "Error al generar el plan de repaso");
//     } finally {
//       setLoading(false);
//     }
//   }

//   return (
//     <section className="mt-10 space-y-6">
//       <header className="space-y-1">
//         <h2 className="text-lg font-semibold text-neutral-50">
//           Plan de repaso inteligente
//         </h2>
//         <p className="text-sm text-neutral-400">
//           Genera un plan de estudio basado en tus PDFs indexados. Ideal para
//           organizar tu semana de estudio con bloques diarios.
//         </p>
//       </header>

//       {/* Formulario */}
//       <form
//         onSubmit={handleGenerate}
//         className="space-y-4 rounded-2xl border border-neutral-800 bg-neutral-950/60 p-4"
//       >
//         <div className="space-y-2">
//           <label className="text-sm font-medium text-neutral-200">
//             Tema o materia a estudiar
//           </label>
//           <textarea
//             value={tema}
//             onChange={(e) => setTema(e.target.value)}
//             rows={2}
//             placeholder="Ej: Fundamentos de Inteligencia Artificial, módulo de procrastinación, etc."
//             className="w-full rounded-2xl border border-neutral-800 bg-neutral-950 px-3 py-2 text-sm text-neutral-100 placeholder:text-neutral-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
//           />
//         </div>

//         <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
//           <div className="space-y-1">
//             <label className="text-xs font-medium text-neutral-400">
//               Fecha de inicio (opcional)
//             </label>
//             <input
//               type="date"
//               value={fechaInicio}
//               onChange={(e) => setFechaInicio(e.target.value)}
//               className="rounded-xl border border-neutral-800 bg-neutral-950 px-3 py-1.5 text-sm text-neutral-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
//             />
//           </div>

//           <div className="flex-1" />

//           <button
//             type="submit"
//             disabled={!tema || loading}
//             className="rounded-full bg-indigo-500 px-5 py-2 text-sm font-medium text-white transition hover:bg-indigo-400 disabled:bg-neutral-800 disabled:text-neutral-500"
//           >
//             {loading ? "Generando plan..." : "Generar plan de repaso"}
//           </button>
//         </div>

//         <p className="text-xs text-neutral-500">
//           El plan se genera usando tus documentos ya indexados en Qdrant. Puedes
//           subir más PDFs desde la pestaña{" "}
//           <span className="font-semibold text-neutral-300">Documentos</span>.
//         </p>

//         {error && (
//           <p className="mt-2 rounded-xl border border-red-800/60 bg-red-950/40 px-3 py-2 text-xs text-red-300">
//             {error}
//           </p>
//         )}
//       </form>

//       {/* Resultado del plan */}
//       {plan && (
//         <div className="space-y-4">
//           <div className="space-y-1">
//             <h3 className="text-sm font-semibold text-neutral-100">
//               Plan generado para:{" "}
//               <span className="font-normal text-neutral-200">{plan.tema}</span>
//             </h3>
//             <p className="text-xs text-neutral-500">
//               Fecha de inicio:{" "}
//               <span className="font-medium text-neutral-300">
//                 {plan.fecha_inicio}
//               </span>
//             </p>
//           </div>

//           {plan.bloques && plan.bloques.length > 0 ? (
//             <div className="grid gap-3 md:grid-cols-2">
//               {plan.bloques.map((bloque: BloqueRepaso, idx: number) => (
//                 <div
//                   key={`${bloque.dia}-${idx}`}
//                   className="space-y-2 rounded-2xl border border-neutral-800 bg-neutral-950/70 p-3"
//                 >
//                   <p className="text-xs font-semibold text-neutral-100">
//                     Día {bloque.dia} · {bloque.titulo}
//                   </p>
//                   <p className="text-xs text-neutral-300 whitespace-pre-wrap">
//                     {bloque.descripcion}
//                   </p>

//                   <div className="flex flex-wrap items-center gap-2 text-[11px] text-neutral-500">
//                     {bloque.duracion_minutos && (
//                       <span className="rounded-full border border-neutral-800 bg-neutral-900 px-2 py-0.5">
//                         ⏱ {bloque.duracion_minutos} minutos
//                       </span>
//                     )}
//                     {bloque.recursos &&
//                       bloque.recursos.slice(0, 3).map((r, i) => (
//                         <span
//                           key={i}
//                           className="rounded-full border border-neutral-800 bg-neutral-900 px-2 py-0.5"
//                         >
//                           📎 {r}
//                         </span>
//                       ))}
//                   </div>
//                 </div>
//               ))}
//             </div>
//           ) : (
//             <p className="text-xs text-neutral-500">
//               El backend no devolvió bloques de repaso. Revisa el formato de la
//               respuesta de <code>/plan-repaso</code>.
//             </p>
//           )}
//         </div>
//       )}
//     </section>
//   );
// }

//NUEVO

"use client";

import { useState } from "react";
import { createPlan } from "@/lib/api";

interface SesionRepaso {
  tipo: string;
  fecha: string;
  descripcion: string | { type: string; text: string; extras?: any }[];
}

interface PlanRepaso {
  tema: string;
  fecha_inicio: string;
  sesiones: SesionRepaso[];
}

export function PlanSection() {
  const [tema, setTema] = useState("");
  const [fecha, setFecha] = useState("");
  const [loading, setLoading] = useState(false);

  const [plan, setPlan] = useState<PlanRepaso | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate() {
    if (!tema) return;

    setLoading(true);
    setPlan(null);
    setError(null);

    try {
      const p = await createPlan(tema, fecha || undefined);
      setPlan(p);
    } catch (e: any) {
      setError("Error generando el plan de repaso");
    } finally {
      setLoading(false);
    }
  }

  // Render de descripción por sesión
  function renderDescripcion(desc: SesionRepaso["descripcion"]) {
    if (typeof desc === "string") {
      return (
        <p className="text-sm whitespace-pre-line text-neutral-200">{desc}</p>
      );
    }

    // Es un array de bloques
    return desc.map((b, i) => (
      <div key={i} className="space-y-2">
        <p className="text-sm whitespace-pre-line text-neutral-200">
          {b.text}
        </p>

        {b.extras ? (
          <pre className="text-[10px] bg-neutral-900/50 p-2 rounded-xl text-neutral-400 overflow-x-auto">
            {JSON.stringify(b.extras, null, 2)}
          </pre>
        ) : null}
      </div>
    ));
  }

  return (
    <section className="space-y-6 border-t border-neutral-900 pt-10">
      <h2 className="text-xl font-semibold tracking-tight">
        Plan de repaso inteligente
      </h2>

      <p className="text-sm text-neutral-400 max-w-2xl">
        Genera un plan de estudio basado en tus PDFs indexados en Qdrant.  
        Ideal para estudiar de forma diaria y estructurada.
      </p>

      {/* Formulario */}
      <div className="space-y-3 rounded-2xl border border-neutral-800 bg-neutral-950/60 p-4">
        <div className="flex flex-col gap-3">
          <input
            type="text"
            placeholder="Tema o materia (ej: Álgebra lineal, Inteligencia Artificial...)"
            className="rounded-xl bg-neutral-900 px-3 py-2 text-sm text-neutral-100 border border-neutral-800"
            value={tema}
            onChange={(e) => setTema(e.target.value)}
          />

          <input
            type="date"
            className="rounded-xl bg-neutral-900 px-3 py-2 text-sm text-neutral-100 border border-neutral-800 w-44"
            value={fecha}
            onChange={(e) => setFecha(e.target.value)}
          />

          <button
            onClick={handleGenerate}
            disabled={loading || !tema}
            className="rounded-full bg-indigo-500 px-5 py-2 text-sm font-medium text-white disabled:bg-neutral-700"
          >
            {loading ? "Generando plan..." : "Generar plan de repaso"}
          </button>
        </div>

        {error && (
          <p className="text-xs text-red-400 bg-red-950/40 border border-red-900/60 rounded-xl px-3 py-2">
            {error}
          </p>
        )}
      </div>

      {/* Render del plan */}
      {plan && (
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-neutral-100">
              Plan generado para: {plan.tema}
            </h3>
            <p className="text-sm text-neutral-400">
              Fecha de inicio: {plan.fecha_inicio}
            </p>
          </div>

          <div className="space-y-4">
            {plan.sesiones.map((s, i) => (
              <div
                key={i}
                className="rounded-2xl border border-neutral-800 bg-neutral-950/70 p-4 space-y-2"
              >
                <h4 className="font-medium text-neutral-100">
                  {s.tipo} — {s.fecha}
                </h4>

                {renderDescripcion(s.descripcion)}
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
