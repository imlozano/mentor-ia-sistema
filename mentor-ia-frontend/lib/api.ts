// // lib/api.ts
// export const BACKEND_URL =
//   process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";

// // Llamar el endpoint RAG
// export async function askQuery(pregunta: string) {
//   const res = await fetch(`${BACKEND_URL}/query`, {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ pregunta }),
//   });

//   if (!res.ok) throw new Error("Error en la consulta RAG");
//   return res.json();
// }

// // Llamar el endpoint OCR
// export async function ocrImage(formData: FormData) {
//   const res = await fetch(`${BACKEND_URL}/ocr-imagen`, {
//     method: "POST",
//     body: formData,
//   });

//   if (!res.ok) throw new Error("Error en OCR");
//   return res.json();
// }



// -------- /ocr-imagen -------- Este paso un formdate no un file
// export async function ocrImage(file: File) {
//   const formData = new FormData();
//   formData.append("file", file);

//   const res = await fetch(`${BACKEND_URL}/ocr-imagen`, {
//     method: "POST",
//     body: formData,
//   });

//   if (!res.ok) {
//     const text = await res.text().catch(() => "");
//     console.error("Error en /ocr-imagen:", res.status, text);
//     throw new Error("Error al consultar /ocr-imagen");
//   }

//   return res.json();
// }


// export async function ocrImage(formData: FormData) {

//   const res = await fetch(`${BACKEND_URL}/ocr-imagen`, {
//     method: "POST",
//     body: formData,
//   });

//   if (!res.ok) {
//     const text = await res.text().catch(() => "");
//     console.error("Error en /ocr-imagen:", res.status, text);
//     throw new Error("Error al procesar la imagen");
//   }

//   return res.json();
// }






// lib/api.ts

// import type { DocumentoInfo, UploadPdfResponse } from "@/lib/types";


// const BACKEND_URL =
//   process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000";

// // -------- /query --------
// export async function askQuery(pregunta: string) {
//   const res = await fetch(`${BACKEND_URL}/query`, {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ pregunta }),
//   });

//   if (!res.ok) {
//     const text = await res.text().catch(() => "");
//     console.error("Error en /query:", res.status, text);
//     throw new Error("Error al consultar /query");
//   }

//   return res.json();
// }

// // -------- /plan-repaso --------
// export async function createPlan(tema: string, fechaInicio?: string) {
//   const res = await fetch(`${BACKEND_URL}/plan-repaso`, {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify(
//       fechaInicio ? { tema, fecha_inicio: fechaInicio } : { tema }
//     ),
//   });

//   if (!res.ok) {
//     const text = await res.text().catch(() => "");
//     console.error("Error en /plan-repaso:", res.status, text);
//     throw new Error("Error al consultar /plan-repaso");
//   }

//   return res.json();
// }

// // -------- /ocr-imagen --------
// export async function ocrImage(file: File) {
//   const formData = new FormData();
//   formData.append("file", file);

//   const res = await fetch(`${BACKEND_URL}/ocr-imagen`, {
//     method: "POST",
//     body: formData,
//   });

//   if (!res.ok) {
//     const text = await res.text().catch(() => "");
//     console.error("Error en /ocr-imagen:", res.status, text);
//     throw new Error("Error al procesar la imagen");
//   }

//   return res.json();
// }

// // nuevo
// // -------- /docs --------
// export async function listDocs(): Promise<DocumentoInfo[]> {
//   const res = await fetch(`${BACKEND_URL}/docs`, {
//     method: "GET",
//   });

//   if (!res.ok) {
//     const text = await res.text().catch(() => "");
//     console.error("Error en /docs:", res.status, text);
//     throw new Error("Error al listar documentos");
//   }

//   return res.json();
// }

// // -------- /upload-pdf --------
// export async function uploadPdf(file: File): Promise<UploadPdfResponse> {
//   const formData = new FormData();
//   formData.append("file", file);

//   const res = await fetch(`${BACKEND_URL}/upload-pdf`, {
//     method: "POST",
//     body: formData,
//   });

//   if (!res.ok) {
//     const text = await res.text().catch(() => "");
//     console.error("Error en /upload-pdf:", res.status, text);
//     throw new Error("Error al subir el PDF");
//   }

//   return res.json();
// }

// //NUEVO
// import type { DocumentosIndexadosResponse } from "./types";

// // -------- /documentos-indexados --------
// export async function getIndexedDocuments(): Promise<DocumentosIndexadosResponse> {
//   const res = await fetch(`${BACKEND_URL}/documentos-indexados`, {
//     method: "GET",
//   });

//   if (!res.ok) {
//     const text = await res.text().catch(() => "");
//     console.error("Error en /documentos-indexados:", res.status, text);
//     throw new Error("Error al consultar documentos indexados");
//   }

//   return res.json();
// }



// // lib/api.ts
// import type {
//   UploadPdfResponse,
//   DocumentosIndexadosResponse,
// } from "@/lib/types";

// const BACKEND_URL =
//   process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000";

// // -------- /query --------
// export async function askQuery(pregunta: string) {
//   const res = await fetch(`${BACKEND_URL}/query`, {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ pregunta }),
//   });

//   if (!res.ok) {
//     const text = await res.text().catch(() => "");
//     console.error("Error en /query:", res.status, text);
//     throw new Error("Error al consultar /query");
//   }

//   return res.json();
// }

// // -------- /plan-repaso --------
// export async function createPlan(tema: string, fechaInicio?: string) {
//   const res = await fetch(`${BACKEND_URL}/plan-repaso`, {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify(
//       fechaInicio ? { tema, fecha_inicio: fechaInicio } : { tema },
//     ),
//   });

//   if (!res.ok) {
//     const text = await res.text().catch(() => "");
//     console.error("Error en /plan-repaso:", res.status, text);
//     throw new Error("Error al consultar /plan-repaso");
//   }

//   return res.json();
// }

// // -------- /ocr-imagen --------
// export async function ocrImage(file: File) {
//   const formData = new FormData();
//   formData.append("file", file);

//   const res = await fetch(`${BACKEND_URL}/ocr-imagen`, {
//     method: "POST",
//     body: formData,
//   });

//   if (!res.ok) {
//     const text = await res.text().catch(() => "");
//     console.error("Error en /ocr-imagen:", res.status, text);
//     throw new Error("Error al procesar la imagen");
//   }

//   return res.json();
// }

// // -------- /upload-pdf --------
// export async function uploadPdf(file: File): Promise<UploadPdfResponse> {
//   const formData = new FormData();
//   formData.append("file", file);

//   const res = await fetch(`${BACKEND_URL}/upload-pdf`, {
//     method: "POST",
//     body: formData,
//   });

//   if (!res.ok) {
//     const text = await res.text().catch(() => "");
//     console.error("Error en /upload-pdf:", res.status, text);
//     throw new Error("Error al subir el PDF");
//   }

//   return res.json();
// }

// // -------- /documentos-indexados --------
// export async function getIndexedDocuments(): Promise<DocumentosIndexadosResponse> {
//   const res = await fetch(`${BACKEND_URL}/documentos-indexados`, {
//     method: "GET",
//   });

//   if (!res.ok) {
//     const text = await res.text().catch(() => "");
//     console.error("Error en /documentos-indexados:", res.status, text);
//     throw new Error("Error al consultar documentos indexados");
//   }

//   return res.json();
// }


// lib/api.ts
import type {
  DocumentoInfo,
  UploadPdfResponse,
  DocumentosIndexadosResponse,
  PlanRepasoResponse,
} from "@/lib/types";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000";

// -------- /query --------
export async function askQuery(pregunta: string) {
  const res = await fetch(`${BACKEND_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pregunta }),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    console.error("Error en /query:", res.status, text);
    throw new Error("Error al consultar /query");
  }

  return res.json();
}

// antes
// // -------- /plan-repaso --------
// export async function createPlan(tema: string, fechaInicio?: string) {
//   const res = await fetch(`${BACKEND_URL}/plan-repaso`, {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify(
//       fechaInicio ? { tema, fecha_inicio: fechaInicio } : { tema }
//     ),
//   });

//   if (!res.ok) {
//     const text = await res.text().catch(() => "");
//     console.error("Error en /plan-repaso:", res.status, text);
//     throw new Error("Error al consultar /plan-repaso");
//   }

//   return res.json();
// }


// -------- /plan-repaso -------- NUEVO
export async function createPlan(
  tema: string,
  fechaInicio?: string
): Promise<PlanRepasoResponse> {
  const res = await fetch(`${BACKEND_URL}/plan-repaso`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(
      fechaInicio ? { tema, fecha_inicio: fechaInicio } : { tema }
    ),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    console.error("Error en /plan-repaso:", res.status, text);
    throw new Error("Error al consultar /plan-repaso");
  }

  return res.json();
}


// -------- /ocr-imagen --------
export async function ocrImage(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BACKEND_URL}/ocr-imagen`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    console.error("Error en /ocr-imagen:", res.status, text);
    throw new Error("Error al procesar la imagen");
  }

  return res.json();
}

// -------- /upload-pdf --------
export async function uploadPdf(file: File): Promise<UploadPdfResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BACKEND_URL}/upload-pdf`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    console.error("Error en /upload-pdf:", res.status, text);
    throw new Error("Error al subir el PDF");
  }

  return res.json();
}

// -------- /documentos-indexados --------
export async function getIndexedDocuments(): Promise<DocumentosIndexadosResponse> {
  const res = await fetch(`${BACKEND_URL}/documentos-indexados`, {
    method: "GET",
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    console.error("Error en /documentos-indexados:", res.status, text);
    throw new Error("Error al consultar documentos indexados");
  }

  return res.json();
}

