// // lib/types.ts

// // --- Fuentes usadas en /query ---
// export interface Fuente {
//   texto: string;
//   source_path: string;
//   chunk_index: number;
//   score: number;
// }

// export interface QueryResponse {
//   pregunta: string;
//   respuesta: string;
//   origen: string;
//   detalle_origen: string;
//   fuentes: Fuente[];
// }

// // --- OCR ---
// export interface OCRResponse {
//   texto: string;
// }

// // --- Documentos en /docs ---
// export interface DocumentoInfo {
//   nombre: string;
//   size_bytes?: number;
//   tipo?: string;
// }

// export interface UploadPdfResponse {
//   filename: string;
//   chunks_ingresados: number;
// }

// // Documentos indexados en Qdrant
// export interface DocumentoIndexadoInfo extends DocumentoInfo {
//   total_chunks: number;
// }

// export interface DocumentosIndexadosResponse {
//   total_chunks: number;
//   documentos: DocumentoIndexadoInfo[];
// }

// // --- Plan de repaso ---

// export interface BloqueRepaso {
//   dia: number;               // Día relativo (1, 2, 3…)
//   titulo: string;            // Título del bloque
//   descripcion: string;       // Contenido del día
//   duracion_minutos?: number;
//   recursos?: string[];
// }

// // *** MUY IMPORTANTE ***
// // Esta interfaz DEBE coincidir EXACTAMENTE con lo que tu backend devuelve.
// // Tu backend devuelve: tema, fecha_inicio y SESIONES[]
// // así que debes usar SESIONES, NO “bloques”.

// export interface SesionRepaso {
//   tipo: string;              // Ej: D+1, D+7, D+30
//   fecha: string;             // Fecha exacta
//   descripcion: any;          // Puede ser string o un objeto con "type" y "text"
// }

// export interface PlanRepasoResponse {
//   tema: string;
//   fecha_inicio: string;
//   sesiones: SesionRepaso[];
// }

// lib/types.ts

// ---------- RAG / consulta ----------

export interface Fuente {
  texto: string;
  source_path: string;
  chunk_index: number;
  score: number;
}

export interface QueryResponse {
  pregunta: string;
  respuesta: string;
  origen: string;
  detalle_origen: string;
  fuentes: Fuente[];
}

// ---------- OCR ----------

export interface OCRResponse {
  texto: string;
}

// ---------- Gestión de documentos (PDFs / imágenes) ----------

export interface DocumentoInfo {
  nombre: string;
  size_bytes?: number;
  tipo?: string;
}

export interface UploadPdfResponse {
  filename: string;
  chunks_ingresados: number;
}

// Documentos indexados en Qdrant
export interface DocumentoIndexadoInfo extends DocumentoInfo {
  total_chunks: number;
}

export interface DocumentosIndexadosResponse {
  total_chunks: number;
  documentos: DocumentoIndexadoInfo[];
}

// ---------- Plan de repaso ----------

// Bloques de descripción especiales que a veces devuelve /plan-repaso
// (cuando la descripción viene como array de objetos)
export interface SesionDescripcionBlock {
  type: string;
  text: string;
  extras?: any; // aquí podríamos tipar mejor más adelante si hace falta
}

export interface SesionRepaso {
  tipo: string;  // D+1, D+7, etc.
  fecha: string; // 2025-11-22, etc.
  // A veces el backend devuelve string, a veces array de bloques {type, text, extras}
  descripcion: string | SesionDescripcionBlock[];
}

export interface PlanRepasoResponse {
  tema: string;
  fecha_inicio: string;
  sesiones: SesionRepaso[];
}


