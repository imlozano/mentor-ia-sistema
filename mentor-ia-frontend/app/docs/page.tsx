// "use client";

// import { useEffect, useState } from "react";
// import { listDocs, uploadPdf } from "@/lib/api";
// import type { DocumentoInfo } from "@/lib/types";

// export default function DocsPage() {
//   const [docs, setDocs] = useState<DocumentoInfo[]>([]);
//   const [file, setFile] = useState<File | null>(null);
//   const [loading, setLoading] = useState(false);
//   const [message, setMessage] = useState<string | null>(null);
//   const [error, setError] = useState<string | null>(null);

//   async function cargarDocumentos() {
//     try {
//       const data = await listDocs();
//       setDocs(data);
//     } catch (e: any) {
//       console.error(e);
//       setError(e?.message ?? "Error al cargar documentos");
//     }
//   }

//   useEffect(() => {
//     cargarDocumentos();
//   }, []);

//   async function handleUpload() {
//     if (!file || loading) return;
//     setLoading(true);
//     setError(null);
//     setMessage(null);

//     try {
//       const res = await uploadPdf(file);
//       setMessage(
//         `Se subió "${res.filename}" y se ingestaron ${res.chunks_ingresados} chunks.`
//       );
//       setFile(null);
//       await cargarDocumentos();
//     } catch (e: any) {
//       setError(e?.message ?? "Error al subir el PDF");
//     } finally {
//       setLoading(false);
//     }
//   }

//   function formatSize(bytes: number) {
//     if (bytes < 1024) return `${bytes} B`;
//     if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
//     return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
//   }

//   return (
//     <div className="min-h-screen w-full">
//       <div className="mx-auto flex w-full max-w-4xl flex-col gap-8 px-4 py-10">
//         <header className="space-y-2">
//           <h1 className="text-2xl font-semibold text-neutral-50">
//             Gestor de documentos
//           </h1>
//           <p className="text-sm text-neutral-400">
//             Sube tus PDFs (apuntes, guías, diapositivas) y el sistema los
//             indexará en Qdrant. Luego podrás hacer preguntas en el asistente de
//             estudio usando este material.
//           </p>
//         </header>

//         {/* Subida de PDF */}
//         <section className="space-y-3 rounded-2xl border border-neutral-800 bg-neutral-950/60 p-4">
//           <h2 className="text-sm font-medium text-neutral-200">
//             Subir nuevo PDF
//           </h2>
//           <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
//             <input
//               type="file"
//               accept="application/pdf"
//               onChange={(e) => setFile(e.target.files?.[0] ?? null)}
//               className="text-xs text-neutral-400 file:mr-3 file:rounded-full file:border-0 file:bg-neutral-800 file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-neutral-100 hover:file:bg-neutral-700"
//             />
//             <button
//               type="button"
//               onClick={handleUpload}
//               disabled={!file || loading}
//               className="rounded-full bg-indigo-500 px-5 py-1.5 text-xs font-medium text-white transition hover:bg-indigo-400 disabled:bg-neutral-800 disabled:text-neutral-500"
//             >
//               {loading ? "Subiendo e indexando..." : "Subir e indexar"}
//             </button>
//           </div>
//           <p className="text-xs text-neutral-500">
//             Al subir un PDF se volverá a ejecutar la ingesta sobre todos los
//             documentos de <code className="rounded bg-neutral-900 px-1 py-0.5">data/ejemplos</code>.
//           </p>

//           {message && (
//             <p className="mt-2 rounded-xl border border-emerald-800/60 bg-emerald-950/40 px-3 py-2 text-xs text-emerald-300">
//               {message}
//             </p>
//           )}

//           {error && (
//             <p className="mt-2 rounded-xl border border-red-800/60 bg-red-950/40 px-3 py-2 text-xs text-red-300">
//               {error}
//             </p>
//           )}
//         </section>

//         {/* Lista de documentos */}
//         <section className="space-y-3">
//           <h2 className="text-sm font-medium text-neutral-200">
//             Documentos indexados
//           </h2>

//           {docs.length === 0 ? (
//             <p className="text-xs text-neutral-500">
//               No se han encontrado documentos en{" "}
//               <code className="rounded bg-neutral-900 px-1 py-0.5">
//                 data/ejemplos
//               </code>
//               . Sube un PDF para empezar.
//             </p>
//           ) : (
//             <div className="grid gap-3 md:grid-cols-2">
//               {docs.map((doc) => (
//                 <div
//                   key={doc.nombre}
//                   className="space-y-1 rounded-2xl border border-neutral-800 bg-neutral-950/70 p-3"
//                 >
//                   <p className="text-xs font-medium text-neutral-100 truncate">
//                     {doc.nombre}
//                   </p>
//                   <p className="text-[11px] text-neutral-500">
//                     Tipo: {doc.tipo.toUpperCase()} · Tamaño:{" "}
//                     {formatSize(doc.size_bytes)}
//                   </p>
//                   <p className="text-[11px] text-neutral-500">
//                     Estos documentos se usan como base para el asistente de
//                     estudio y el plan de repaso.
//                   </p>
//                 </div>
//               ))}
//             </div>
//           )}
//         </section>
//       </div>
//     </div>
//   );
// }

"use client";

import { useEffect, useState } from "react";
import { uploadPdf, getIndexedDocuments } from "@/lib/api";
import type { DocumentoIndexadoInfo } from "@/lib/types";

export default function DocsPage() {
  const [docs, setDocs] = useState<DocumentoIndexadoInfo[]>([]);
  const [totalChunks, setTotalChunks] = useState<number | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function cargarDocumentos() {
    try {
      const data = await getIndexedDocuments();
      setDocs(data.documentos || []);
      setTotalChunks(data.total_chunks ?? null);
      setError(null);
    } catch (e: any) {
      console.error(e);
      setError(e?.message ?? "Error al cargar documentos indexados");
    }
  }

  useEffect(() => {
    cargarDocumentos();
  }, []);

  async function handleUpload() {
    if (!file || loading) return;
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const res = await uploadPdf(file);
      setMessage(
        `Se subió "${res.filename}" y se ingestaron ${res.chunks_ingresados} chunks.`,
      );
      setFile(null);
      await cargarDocumentos();
    } catch (e: any) {
      setError(e?.message ?? "Error al subir el PDF");
    } finally {
      setLoading(false);
    }
  }

  function formatSize(bytes: number) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  return (
    <div className="min-h-screen w-full">
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-8 px-4 py-10">
        <header className="space-y-2">
          <h1 className="text-2xl font-semibold text-neutral-50">
            Gestor de documentos
          </h1>
          <p className="text-sm text-neutral-400">
            Sube tus PDFs (apuntes, guías, diapositivas) y el sistema los
            indexará en Qdrant. Luego podrás hacer preguntas en el asistente de
            estudio usando este material.
          </p>
          {totalChunks !== null && (
            <p className="text-xs text-neutral-500">
              Actualmente hay{" "}
              <span className="font-semibold text-neutral-200">
                {totalChunks}
              </span>{" "}
              chunks indexados en la base vectorial.
            </p>
          )}
        </header>

        {/* Subida de PDF */}
        <section className="space-y-3 rounded-2xl border border-neutral-800 bg-neutral-950/60 p-4">
          <h2 className="text-sm font-medium text-neutral-200">
            Subir nuevo PDF
          </h2>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="text-xs text-neutral-400 file:mr-3 file:rounded-full file:border-0 file:bg-neutral-800 file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-neutral-100 hover:file:bg-neutral-700"
            />
            <button
              type="button"
              onClick={handleUpload}
              disabled={!file || loading}
              className="rounded-full bg-indigo-500 px-5 py-1.5 text-xs font-medium text-white transition hover:bg-indigo-400 disabled:bg-neutral-800 disabled:text-neutral-500"
            >
              {loading ? "Subiendo e indexando..." : "Subir e indexar"}
            </button>
          </div>
          <p className="text-xs text-neutral-500">
            Cada vez que subas un PDF, el backend lo copiará al directorio de
            trabajo y reingestará el contenido en Qdrant.
          </p>

          {message && (
            <p className="mt-2 rounded-xl border border-emerald-800/60 bg-emerald-950/40 px-3 py-2 text-xs text-emerald-300">
              {message}
            </p>
          )}

          {error && (
            <p className="mt-2 rounded-xl border border-red-800/60 bg-red-950/40 px-3 py-2 text-xs text-red-300">
              {error}
            </p>
          )}
        </section>

        {/* Lista de documentos */}
        <section className="space-y-3">
          <h2 className="text-sm font-medium text-neutral-200">
            Documentos indexados
          </h2>

          {docs.length === 0 ? (
            <p className="text-xs text-neutral-500">
              Aún no hay documentos reportados por el backend. Sube un PDF para
              empezar.
            </p>
          ) : (
            <div className="grid gap-3 md:grid-cols-2">
              {/* {docs.map((doc) => (
                <div
                  key={doc.nombre}
                  className="space-y-1 rounded-2xl border border-neutral-800 bg-neutral-950/70 p-3"
                >
                  <p className="truncate text-xs font-medium text-neutral-100">
                    {doc.nombre}
                  </p>
                  <p className="text-[11px] text-neutral-500">
                    Tipo: {doc.tipo.toUpperCase()} · Tamaño:{" "}
                    {formatSize(doc.size_bytes)}
                  </p>
                  <p className="text-[11px] text-neutral-500">
                    Chunks indexados de este documento:{" "}
                    <span className="font-medium text-neutral-300">
                      {doc.total_chunks}
                    </span>
                  </p>
                  <p className="text-[11px] text-neutral-500">
                    Estos documentos se usan como base para el asistente de
                    estudio y el plan de repaso.
                  </p>
                </div>
              ))} */}
              {docs.map((doc) => {
                const tipoText = doc.tipo
                    ? doc.tipo.toUpperCase()
                    : "DESCONOCIDO";

                const sizeText =
                    typeof doc.size_bytes === "number"
                    ? formatSize(doc.size_bytes)
                    : "N/A";

            return (
                <div
                key={doc.nombre}
                className="space-y-1 rounded-2xl border border-neutral-800 bg-neutral-950/70 p-3"
                >
                <p className="text-xs font-medium text-neutral-100 truncate">
                    {doc.nombre}
                </p>
                <p className="text-[11px] text-neutral-500">
                    Tipo: {tipoText} · Tamaño: {sizeText}
                </p>
                <p className="text-[11px] text-neutral-500">
                    Estos documentos se usan como base para el asistente de
                    estudio y el plan de repaso.
                </p>
                </div>
                );
            })}

            </div>
          )}
        </section>
      </div>
    </div>
  );
}

