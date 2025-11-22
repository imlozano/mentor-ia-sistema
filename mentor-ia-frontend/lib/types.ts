// // lib/types.ts

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
// // Nuevo interfaz para la respuesta OCR
// export interface OCRResponse {
//   texto: string;
// }

// export interface DocumentoInfo {
//   nombre: string;
//   size_bytes?: number;
//   tipo?: string;
// }

// export interface UploadPdfResponse {
//   filename: string;
//   chunks_ingresados: number;
// }

// //nuevo
// export interface DocumentoIndexadoInfo extends DocumentoInfo {
//   total_chunks: number;
// }

// export interface DocumentosIndexadosResponse {
//   total_chunks: number;
//   documentos: DocumentoIndexadoInfo[];
// }



// // --- Plan de repaso ---

// export interface BloqueRepaso {
//   dia: number;              // Día relativo (1, 2, 3, ...)
//   titulo: string;           // Título del bloque
//   descripcion: string;      // Qué se estudia ese día
//   duracion_minutos?: number;
//   recursos?: string[];      // Opcional: recursos sugeridos
// }

// // OJO: si tu backend usa otro nombre (por ejemplo "plan" en vez de "bloques"),
// // cambia aquí "bloques" para que coincida.
// export interface PlanRepasoResponse {
//   tema: string;
//   fecha_inicio: string;
//   bloques: BloqueRepaso[];
// }

// // NUEVO
// // export interface DocumentoIndexado {
// //   nombre: string;
// //   ruta: string;
// //   extension: string;
// // }

// // export interface DocumentosIndexadosResponse {
// //   documentos: DocumentoIndexado[];
// // }


// lib/types.ts

// --- Fuentes usadas en /query ---
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

// --- OCR ---
export interface OCRResponse {
  texto: string;
}

// --- Documentos en /docs ---
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

// --- Plan de repaso ---

export interface BloqueRepaso {
  dia: number;               // Día relativo (1, 2, 3…)
  titulo: string;            // Título del bloque
  descripcion: string;       // Contenido del día
  duracion_minutos?: number;
  recursos?: string[];
}

// *** MUY IMPORTANTE ***
// Esta interfaz DEBE coincidir EXACTAMENTE con lo que tu backend devuelve.
// Tu backend devuelve: tema, fecha_inicio y SESIONES[]
// así que debes usar SESIONES, NO “bloques”.

export interface SesionRepaso {
  tipo: string;              // Ej: D+1, D+7, D+30
  fecha: string;             // Fecha exacta
  descripcion: any;          // Puede ser string o un objeto con "type" y "text"
}

export interface PlanRepasoResponse {
  tema: string;
  fecha_inicio: string;
  sesiones: SesionRepaso[];
}


