# """
# agente_extraccion.py

# Agente responsable de:
# - Cargar documentos.
# - Extraer texto.
# - Hacer chunking.
# - Generar embeddings.
# - Guardar en Qdrant.
# """

# from typing import List

# from qdrant_client.models import PointStruct

# from src.extraccion import DocumentoFuente, listar_documentos_ejemplo, extraer_texto_documento
# from src.chunking import chunk_text
# from src.embeddings import (
#     crear_cliente_qdrant,
#     asegurar_coleccion,
#     crear_modelo_embeddings,
#     VectorConfig,
#     generar_embeddings,
# )


# class AgenteExtraccion:
#     def __init__(self) -> None:
#         self.client = crear_cliente_qdrant()
#         self.vector_config = VectorConfig()
#         asegurar_coleccion(self.client, self.vector_config)
#         self.embeddings_model = crear_modelo_embeddings()

#     def ingestar_documentos(self, docs: List[DocumentoFuente] | None = None) -> int:
#         """
#         Punto de entrada para ingestar documentos a la base vectorial.

#         Devuelve el número de chunks almacenados.
#         """
#         if docs is None:
#             docs = listar_documentos_ejemplo()

#         todos_chunks: List[str] = []
#         metadatos: List[dict] = []

#         for doc in docs:
#             texto = extraer_texto_documento(doc)
#             chunks = chunk_text(texto)

#             for idx, ch in enumerate(chunks):
#                 todos_chunks.append(ch)
#                 metadatos.append(
#                     {
#                         "source_path": str(doc.path),
#                         "chunk_index": idx,
#                     }
#                 )

#         if not todos_chunks:
#             return 0

#         # 1. Generar embeddings
#         vectores = generar_embeddings(todos_chunks, self.embeddings_model)

#         # 2. Preparar puntos para Qdrant
#         points = []
#         for i, (vector, metadata) in enumerate(zip(vectores, metadatos)):
#             points.append(
#                 PointStruct(
#                     id=i,
#                     vector=vector,
#                     payload={
#                         "text": todos_chunks[i],
#                         **metadata,
#                     },
#                 )
#             )

#         # 3. Upsert en Qdrant
#         self.client.upsert(
#             collection_name=self.vector_config.collection_name,
#             points=points,
#         )

#         return len(points)


# """
# agente_extraccion.py

# Agente responsable de:
# - Cargar documentos desde src/extraccion.py
# - Extraer texto
# - Hacer chunking
# - Generar embeddings
# - Guardar en Qdrant con la estructura de payload compatible
#   con AgenteRespuesta y AgentePlanRepaso.
# """

# import uuid
# from typing import List

# from qdrant_client.models import PointStruct

# from src.extraccion import (
#     DocumentoFuente,
#     listar_documentos_ejemplo,
#     extraer_texto_documento
# )
# from src.chunking import chunk_text
# from src.embeddings import (
#     crear_cliente_qdrant,
#     asegurar_coleccion,
#     crear_modelo_embeddings,
#     VectorConfig,
#     generar_embeddings,
# )


# class AgenteExtraccion:
#     def __init__(self) -> None:
#         self.client = crear_cliente_qdrant()
#         self.vector_config = VectorConfig()
#         asegurar_coleccion(self.client, self.vector_config)
#         self.embeddings_model = crear_modelo_embeddings()

#     def ingestar_documentos(self, docs: List[DocumentoFuente] | None = None) -> int:
#         """
#         Ingesta documentos hacia la base vectorial.

#         Devuelve:
#             número total de chunks almacenados.
#         """
#         if docs is None:
#             docs = listar_documentos_ejemplo()

#         todos_chunks: List[str] = []
#         metadatos: List[dict] = []

#         for doc in docs:
#             texto = extraer_texto_documento(doc)
#             if not texto:
#                 print(f"[WARN] Documento sin texto: {doc.path}")
#                 continue

#             chunks = chunk_text(texto)
#             if not chunks:
#                 continue

#             for idx, chunk in enumerate(chunks):
#                 todos_chunks.append(chunk)
#                 metadatos.append(
#                     {
#                         "source_path": str(doc.path),
#                         "chunk_index": idx,
#                     }
#                 )

#         if not todos_chunks:
#             return 0

#         # 1) Generar embeddings
#         vectores = generar_embeddings(todos_chunks, self.embeddings_model)

#         puntos: List[PointStruct] = []

#         # 2) Crear puntos con ids únicos y payload consistente
#         for chunk_text, metadata, vector in zip(todos_chunks, metadatos, vectores):
#             punto_id = uuid.uuid4().int >> 64

#             puntos.append(
#                 PointStruct(
#                     id=punto_id,
#                     vector=vector,
#                     payload={
#                         "texto": chunk_text,      # <- estandarizado
#                         "source_path": metadata["source_path"],
#                         "chunk_index": metadata["chunk_index"],
#                     },
#                 )
#             )

#         # 3) Subir a Qdrant
#         self.client.upsert(
#             collection_name=self.vector_config.collection_name,
#             points=puntos,
#         )

#         return len(puntos)

# """
# agente_extraccion.py

# Agente encargado de:
# - Leer PDFs desde una carpeta (por defecto: data/ejemplos).
# - Dividir el contenido en chunks (trozos de texto).
# - Generar embeddings con Gemini.
# - Enviar los puntos a Qdrant con metadatos coherentes con AgenteRespuesta y AgentePlanRepaso.
# """

# import os
# import glob
# import uuid
# from typing import Dict, List, Any

# from dotenv import load_dotenv
# from qdrant_client.models import PointStruct

# from src.embeddings import (
#     VectorConfig,
#     crear_cliente_qdrant,
#     crear_modelo_embeddings,
#     asegurar_coleccion,
# )

# load_dotenv()


# class AgenteExtraccion:
#     def __init__(self) -> None:
#         # 1) Configuración de Qdrant (igual que los otros agentes)
#         self.vector_config = VectorConfig()
#         self.client = crear_cliente_qdrant()

#         # Aseguramos que la colección exista
#         asegurar_coleccion(self.client, self.vector_config)

#         # 2) Modelo de embeddings (Gemini)
#         self.embeddings_model = crear_modelo_embeddings()

#     # ---------------------------------------------------------
#     #  LECTURA DE PDFs
#     # ---------------------------------------------------------
#     def _leer_pdfs_desde_carpeta(
#         self,
#         carpeta: str = "data/ejemplos",
#     ) -> List[Dict[str, Any]]:
#         """
#         Lee todos los PDFs de una carpeta y devuelve una lista de:
#         [
#             {
#                 "source_path": "ruta/al/archivo.pdf",
#                 "texto": "contenido completo del pdf como string"
#             },
#             ...
#         ]
#         """
#         from pypdf import PdfReader  # requiere `pip install pypdf`

#         documentos: List[Dict[str, Any]] = []

#         patron = os.path.join(carpeta, "*.pdf")
#         rutas = glob.glob(patron)

#         for ruta in rutas:
#             try:
#                 reader = PdfReader(ruta)
#                 paginas_texto: List[str] = []

#                 for page in reader.pages:
#                     texto_pagina = page.extract_text() or ""
#                     paginas_texto.append(texto_pagina)

#                 contenido = "\n\n".join(paginas_texto).strip()
#                 if not contenido:
#                     # PDF vacío o sin texto legible
#                     continue

#                 documentos.append(
#                     {
#                         "source_path": ruta,
#                         "texto": contenido,
#                     }
#                 )
#             except Exception as e:
#                 # En producción podrías loguearlo; por ahora lo mostramos en consola
#                 print(f"[WARN] No se pudo leer el PDF {ruta}: {e}")

#         return documentos

#     # ---------------------------------------------------------
#     #  CHUNKING / TROCEADO DE TEXTO
#     # ---------------------------------------------------------
#     def _chunkear_texto(
#         self,
#         texto: str,
#         max_chars: int = 900,
#         overlap: int = 150,
#     ) -> List[str]:
#         """
#         Divide un texto largo en chunks de tamaño máximo `max_chars`,
#         con solapamiento `overlap` entre chunks.

#         Devuelve: lista de strings (cada uno es un chunk).
#         """
#         if not texto:
#             return []

#         chunks: List[str] = []
#         inicio = 0
#         longitud = len(texto)

#         while inicio < longitud:
#             fin = min(inicio + max_chars, longitud)
#             trozo = texto[inicio:fin].strip()
#             if trozo:
#                 chunks.append(trozo)

#             # avance con solapamiento
#             inicio = fin - overlap

#             if inicio < 0:
#                 inicio = 0
#             if inicio >= longitud:
#                 break

#         return chunks

#     # ---------------------------------------------------------
#     #  INGESTA PRINCIPAL
#     # ---------------------------------------------------------
#     def ingestar_documentos(self, carpeta: str = "data/ejemplos") -> int:
#         """
#         Lee PDFs de la carpeta, los trocea, genera embeddings y hace upsert en Qdrant.

#         Devuelve:
#             número total de chunks insertados.
#         """

#         documentos = self._leer_pdfs_desde_carpeta(carpeta)

#         if not documentos:
#             print("[INFO] No se encontraron PDFs para ingestar.")
#             return 0

#         puntos_a_insertar: List[PointStruct] = []
#         total_chunks = 0

#         for doc in documentos:
#             source_path = doc["source_path"]
#             texto = doc["texto"]

#             # 1) Trocear texto en chunks
#             chunks = self._chunkear_texto(texto)
#             if not chunks:
#                 continue

#             # 2) Generar embeddings para los chunks de este documento
#             vectores = self.embeddings_model.embed_documents(chunks)

#             # 3) Construir PointStruct por cada chunk
#             for idx, (chunk_text, vector) in enumerate(zip(chunks, vectores)):
#                 punto_id = uuid.uuid4().int >> 64  # entero grande casi único

#                 payload = {
#                     "texto": chunk_text,        # <- clave que usan AgenteRespuesta y PlanRepaso
#                     "source_path": source_path, # para saber de qué PDF viene
#                     "chunk_index": idx,         # índice del chunk
#                 }

#                 puntos_a_insertar.append(
#                     PointStruct(
#                         id=punto_id,
#                         vector=vector,
#                         payload=payload,
#                     )
#                 )

#             total_chunks += len(chunks)

#         if not puntos_a_insertar:
#             print("[INFO] No se generaron puntos para Qdrant.")
#             return 0

#         # 4) Enviar todo a Qdrant
#         self.client.upsert(
#             collection_name=self.vector_config.collection_name,
#             points=puntos_a_insertar,
#         )

#         print(f"[OK] Se ingresaron {total_chunks} chunks en Qdrant.")
#         return total_chunks




# -------> ESTA VERSION SI FUNCIONA <-------

# """
# agente_extraccion.py

# Agente encargado de:
# - Leer PDFs desde una carpeta (por defecto: data/ejemplos).
# - Dividir el contenido en chunks (trozos de texto).
# - Generar embeddings con Gemini.
# - Enviar los puntos a Qdrant con metadatos coherentes con AgenteRespuesta y AgentePlanRepaso.
# """

# import os
# import glob
# import uuid
# from typing import Dict, List, Any

# from dotenv import load_dotenv
# from qdrant_client.models import PointStruct

# from src.embeddings import (
#     VectorConfig,
#     crear_cliente_qdrant,
#     crear_modelo_embeddings,
# )

# load_dotenv()


# class AgenteExtraccion:
#     def __init__(self) -> None:
#         # 1) Configuración de Qdrant (igual que los otros agentes)
#         self.vector_config = VectorConfig()
#         self.client = crear_cliente_qdrant()

#         # 2) Modelo de embeddings (Gemini)
#         self.embeddings_model = crear_modelo_embeddings()

#     # ---------------------------------------------------------
#     #  LECTURA DE PDFs
#     # ---------------------------------------------------------
#     def _leer_pdfs_desde_carpeta(
#         self,
#         carpeta: str = "data/ejemplos",
#         max_paginas_por_pdf: int = 80,   # <- límite de seguridad
#     ) -> List[Dict[str, Any]]:
#         """
#         Lee todos los PDFs de una carpeta y devuelve una lista de:
#         [
#             {
#                 "source_path": "ruta/al/archivo.pdf",
#                 "texto": "contenido completo del pdf como string"
#             },
#             ...
#         ]
#         """
#         from pypdf import PdfReader  # requiere `pip install pypdf`

#         documentos: List[Dict[str, Any]] = []

#         patron = os.path.join(carpeta, "*.pdf")
#         rutas = glob.glob(patron)

#         print(f"[INGESTA] Buscando PDFs en: {carpeta}")
#         print(f"[INGESTA] PDFs encontrados: {rutas}")

#         for ruta in rutas:
#             print(f"[INGESTA] Leyendo PDF: {ruta}")
#             try:
#                 reader = PdfReader(ruta)
#                 num_paginas = len(reader.pages)
#                 print(f"[INGESTA]  -> Páginas: {num_paginas}")

#                 if num_paginas == 0:
#                     print(f"[WARN] PDF sin páginas legibles: {ruta}")
#                     continue

#                 if num_paginas > max_paginas_por_pdf:
#                     print(
#                         f"[WARN] PDF muy grande ({num_paginas} páginas), "
#                         f"se limita a las primeras {max_paginas_por_pdf}."
#                     )
#                     limite = max_paginas_por_pdf
#                 else:
#                     limite = num_paginas

#                 paginas_texto: List[str] = []
#                 for i in range(limite):
#                     page = reader.pages[i]
#                     texto_pagina = page.extract_text() or ""
#                     paginas_texto.append(texto_pagina)

#                 contenido = "\n\n".join(paginas_texto).strip()
#                 if not contenido:
#                     print(f"[WARN] No se extrajo texto legible de: {ruta}")
#                     continue

#                 documentos.append(
#                     {
#                         "source_path": ruta,
#                         "texto": contenido,
#                     }
#                 )
#                 print(f"[INGESTA]  -> Texto extraído OK ({len(contenido)} caracteres).")

#             except Exception as e:
#                 # En producción podrías loguearlo; por ahora lo mostramos
#                 print(f"[ERROR] No se pudo leer el PDF {ruta}: {e}")

#         print(f"[INGESTA] Total documentos cargados: {len(documentos)}")
#         return documentos

#     # ---------------------------------------------------------
#     #  CHUNKING / TROCEADO DE TEXTO
#     # ---------------------------------------------------------
#     def _chunkear_texto(
#         self,
#         texto: str,
#         max_chars: int = 900,
#         overlap: int = 150,
#         max_chunks_por_doc: int = 200,  # <- límite de seguridad
#     ) -> List[str]:
#         """
#         Divide un texto largo en chunks de tamaño máximo `max_chars`,
#         con solapamiento `overlap` entre chunks.
#         """
#         if not texto:
#             return []

#         chunks: List[str] = []
#         inicio = 0
#         longitud = len(texto)

#         while inicio < longitud and len(chunks) < max_chunks_por_doc:
#             fin = min(inicio + max_chars, longitud)
#             trozo = texto[inicio:fin].strip()
#             if trozo:
#                 chunks.append(trozo)
#             inicio = fin - overlap
#             if inicio < 0:
#                 inicio = 0
#             if inicio >= longitud:
#                 break

#         if len(chunks) == max_chunks_por_doc:
#             print("[WARN] Se alcanzó el máximo de chunks por documento.")

#         return chunks

#     # ---------------------------------------------------------
#     #  INGESTA PRINCIPAL
#     # ---------------------------------------------------------
#     def ingestar_documentos(self, carpeta: str = "data/ejemplos") -> int:
#         """
#         Lee PDFs de la carpeta, los trocea, genera embeddings y hace upsert en Qdrant.

#         Devuelve:
#             número total de chunks insertados.
#         """

#         print("[INGESTA] Iniciando proceso de ingesta...")
#         documentos = self._leer_pdfs_desde_carpeta(carpeta)

#         if not documentos:
#             print("[INFO] No se encontraron PDFs para ingestar.")
#             return 0

#         puntos_a_insertar: List[PointStruct] = []
#         total_chunks = 0

#         for doc in documentos:
#             source_path = doc["source_path"]
#             texto = doc["texto"]

#             print(f"[INGESTA] Chunking del documento: {source_path}")
#             chunks = self._chunkear_texto(texto)
#             print(f"[INGESTA]  -> Chunks generados: {len(chunks)}")

#             if not chunks:
#                 continue

#             # 1) Generar embeddings (en lote)
#             print("[INGESTA]  -> Generando embeddings para los chunks...")
#             vectores = self.embeddings_model.embed_documents(chunks)
#             print("[INGESTA]  -> Embeddings generados.")

#             # 2) Construir PointStruct por cada chunk
#             for idx, (chunk_text, vector) in enumerate(zip(chunks, vectores)):
#                 punto_id = uuid.uuid4().int >> 64  # entero grande casi único

#                 payload = {
#                     "texto": chunk_text,         # <- clave que usan tus agentes
#                     "source_path": source_path,  # <- para rastrear el PDF
#                     "chunk_index": idx,          # <- posición del chunk
#                 }

#                 puntos_a_insertar.append(
#                     PointStruct(
#                         id=punto_id,
#                         vector=vector,
#                         payload=payload,
#                     )
#                 )

#             total_chunks += len(chunks)
#             print(f"[INGESTA]  -> Total de chunks acumulados: {total_chunks}")

#         if not puntos_a_insertar:
#             print("[INFO] No se generaron puntos para Qdrant.")
#             return 0

#         print(f"[INGESTA] Enviando {len(puntos_a_insertar)} puntos a Qdrant...")
#         self.client.upsert(
#             collection_name=self.vector_config.collection_name,
#             points=puntos_a_insertar,
#         )

#         print(f"[OK] Se ingresaron {total_chunks} chunks en Qdrant.")
#         return total_chunks
# --------> ESTA VERSION SI FUNCIONA <-------




# """
# agente_extraccion.py

# Agente encargado de:
# - Leer PDFs e imágenes desde una carpeta (por defecto: data/ejemplos).
# - Dividir el contenido textual en chunks.
# - Generar embeddings con Gemini.
# - Enviar los puntos a Qdrant con metadatos coherentes con AgenteRespuesta y AgentePlanRepaso.
# """

# import os
# import glob
# import uuid
# from typing import Dict, List, Any

# from dotenv import load_dotenv
# from qdrant_client.models import PointStruct
# from pypdf import PdfReader

# from src.embeddings import (
#     VectorConfig,
#     crear_cliente_qdrant,
#     crear_modelo_embeddings,
# )
# from src.ocr_vision import crear_cliente_vision, extraer_texto_imagen_vision  # <- NUEVO

# load_dotenv()


# class AgenteExtraccion:
#     def __init__(self) -> None:
#         # 1) Configuración de Qdrant
#         self.vector_config = VectorConfig()
#         self.client = crear_cliente_qdrant()

#         # 2) Modelo de embeddings (Gemini)
#         self.embeddings_model = crear_modelo_embeddings()

#         # 3) Cliente de Google Vision para OCR en imágenes
#         self.vision_client = crear_cliente_vision()  # <- NUEVO

#     # ---------------------------------------------------------
#     #  UTILIDAD: chunking simple
#     # ---------------------------------------------------------
#     def _chunkear_texto(
#         self,
#         texto: str,
#         max_chars: int = 900,
#         overlap: int = 150,
#         max_chunks: int = 200,
#     ) -> List[str]:
#         if not texto:
#             return []

#         chunks: List[str] = []
#         inicio = 0
#         longitud = len(texto)

#         while inicio < longitud and len(chunks) < max_chunks:
#             fin = min(inicio + max_chars, longitud)
#             trozo = texto[inicio:fin].strip()
#             if trozo:
#                 chunks.append(trozo)

#             inicio = fin - overlap
#             if inicio < 0:
#                 inicio = 0
#             if inicio >= longitud:
#                 break

#         if len(chunks) >= max_chunks:
#             print("[WARN] Se alcanzó el máximo de chunks por documento.")

#         return chunks

#     # ---------------------------------------------------------
#     #  LECTURA DE FUENTES (PDFs + IMÁGENES)
#     # ---------------------------------------------------------
#     def _leer_fuentes_desde_carpeta(
#         self,
#         carpeta: str = "data/ejemplos",
#     ) -> List[Dict[str, Any]]:
#         """
#         Busca PDFs e imágenes en la carpeta y devuelve una lista de:
#         [
#             {
#                 "source_path": "ruta/al/archivo",
#                 "texto": "contenido textual extraído"
#             },
#             ...
#         ]
#         """
#         print(f"[INGESTA] Buscando fuentes en: {carpeta}")

#         patrones = [
#             os.path.join(carpeta, "*.pdf"),
#             os.path.join(carpeta, "*.png"),
#             os.path.join(carpeta, "*.jpg"),
#             os.path.join(carpeta, "*.jpeg"),
#         ]

#         rutas: List[str] = []
#         for patron in patrones:
#             rutas.extend(glob.glob(patron))

#         print(f"[INGESTA] Archivos encontrados: {rutas}")

#         documentos: List[Dict[str, Any]] = []

#         for ruta in rutas:
#             ext = os.path.splitext(ruta)[1].lower()

#             if ext == ".pdf":
#                 print(f"[INGESTA] Leyendo PDF: {ruta}")
#                 try:
#                     reader = PdfReader(ruta)
#                     paginas_texto: List[str] = []
#                     for page in reader.pages:
#                         texto_pagina = page.extract_text() or ""
#                         paginas_texto.append(texto_pagina)

#                     contenido = "\n\n".join(paginas_texto).strip()
#                     print(
#                         f"[INGESTA]  -> Páginas: {len(reader.pages)} | "
#                         f"Texto extraído: {len(contenido)} caracteres."
#                     )
#                     if not contenido:
#                         # PDF sin texto legible (ej. escaneado sin OCR interno)
#                         print(
#                             "[WARN] PDF sin texto extraíble por pypdf. "
#                             "Más adelante podremos manejar esto con Vision (OCR para PDF)."
#                         )
#                         continue

#                     documentos.append(
#                         {
#                             "source_path": ruta,
#                             "texto": contenido,
#                         }
#                     )
#                 except Exception as e:
#                     print(f"[WARN] No se pudo leer el PDF {ruta}: {e}")

#             elif ext in {".png", ".jpg", ".jpeg"}:
#                 print(f"[INGESTA] Leyendo imagen para OCR: {ruta}")
#                 try:
#                     texto = extraer_texto_imagen_vision(
#                         ruta_imagen=ruta,
#                         client=self.vision_client,
#                     ).strip()

#                     print(
#                         f"[INGESTA]  -> Texto OCR extraído: {len(texto)} caracteres."
#                     )

#                     if not texto:
#                         print(
#                             f"[WARN] La imagen {ruta} no produjo texto con Vision."
#                         )
#                         continue

#                     documentos.append(
#                         {
#                             "source_path": ruta,
#                             "texto": texto,
#                         }
#                     )
#                 except Exception as e:
#                     print(f"[WARN] Error usando Vision OCR en {ruta}: {e}")

#             else:
#                 # Extensión no soportada (por ahora)
#                 print(f"[INGESTA] Tipo de archivo no soportado, se ignora: {ruta}")

#         print(f"[INGESTA] Total fuentes con texto: {len(documentos)}")
#         return documentos

#     # ---------------------------------------------------------
#     #  INGESTA PRINCIPAL
#     # ---------------------------------------------------------
#     def ingestar_documentos(self, carpeta: str = "data/ejemplos") -> int:
#         print("[INGESTA] Iniciando proceso de ingesta...")

#         documentos = self._leer_fuentes_desde_carpeta(carpeta)

#         if not documentos:
#             print("[INFO] No se encontraron documentos/imagenes con texto para ingestar.")
#             return 0

#         puntos_a_insertar: List[PointStruct] = []
#         total_chunks = 0

#         for doc in documentos:
#             source_path = doc["source_path"]
#             texto = doc["texto"]

#             print(f"[INGESTA] Chunking del documento: {source_path}")
#             chunks = self._chunkear_texto(texto)
#             print(f"[INGESTA]  -> Chunks generados: {len(chunks)}")

#             if not chunks:
#                 continue

#             # 1) Embeddings de todos los chunks de este documento
#             print("[INGESTA]  -> Generando embeddings para los chunks...")
#             vectores = self.embeddings_model.embed_documents(chunks)
#             print("[INGESTA]  -> Embeddings generados.")

#             # 2) Crear puntos para Qdrant
#             for idx, (chunk_text, vector) in enumerate(zip(chunks, vectores)):
#                 punto_id = uuid.uuid4().int >> 64

#                 payload = {
#                     "texto": chunk_text,
#                     "source_path": source_path,
#                     "chunk_index": idx,
#                 }

#                 puntos_a_insertar.append(
#                     PointStruct(
#                         id=punto_id,
#                         vector=vector,
#                         payload=payload,
#                     )
#                 )

#             total_chunks += len(chunks)
#             print(f"[INGESTA]  -> Total de chunks acumulados: {total_chunks}")

#         if not puntos_a_insertar:
#             print("[INFO] No se generaron puntos para Qdrant.")
#             return 0

#         print(f"[INGESTA] Enviando {len(puntos_a_insertar)} puntos a Qdrant...")
#         self.client.upsert(
#             collection_name=self.vector_config.collection_name,
#             points=puntos_a_insertar,
#         )
#         print(f"[OK] Se ingresaron {total_chunks} chunks en Qdrant.")
#         return total_chunks



        
        
        
#         # dentro de la clase AgenteExtraccion
#     def _leer_imagenes_desde_carpeta(self, ruta="data/imagenes"):
#         """
#         Lee imágenes de una carpeta, extrae texto con Vision y devuelve una lista:
#         [
#             {
#                 "texto": "...",
#                 "source_path": "...",
#             },
#             ...
#         ]
#         """
#         if not os.path.exists(ruta):
#             print(f"[IMAGENES] No existe la carpeta {ruta}. Saltando.")
#             return []

#         extensiones = [".png", ".jpg", ".jpeg", ".webp"]
#         imagenes = [
#             os.path.join(ruta, f)
#             for f in os.listdir(ruta)
#             if f.lower().endswith(tuple(extensiones))
#         ]

#         resultados = []
#         for img_path in imagenes:
#             try:
#                 print(f"[IMAGENES] Leyendo imagen: {img_path}")
#                 with open(img_path, "rb") as f:
#                     contenido = f.read()

#                 texto = extraer_texto_imagen_vision(contenido)

#                 resultados.append({
#                     "texto": texto,
#                     "source_path": img_path
#                 })

#             except Exception as e:
#                 print(f"[ERROR] Problema leyendo {img_path}: {e}")

#         return resultados



"""
agente_extraccion.py

Agente encargado de:
- Leer PDFs e imágenes desde una carpeta (por defecto: data/ejemplos).
- Dividir el contenido textual en chunks.
- Generar embeddings con Gemini.
- Enviar los puntos a Qdrant con metadatos coherentes con AgenteRespuesta y AgentePlanRepaso.
"""

import os
import glob
import uuid
from typing import Dict, List, Any

from dotenv import load_dotenv
from qdrant_client.models import PointStruct
from pypdf import PdfReader

from src.embeddings import (
    VectorConfig,
    crear_cliente_qdrant,
    crear_modelo_embeddings,
)
from src.ocr_vision import crear_cliente_vision, extraer_texto_imagen_vision  # OCR Vision

load_dotenv()


class AgenteExtraccion:
    def __init__(self) -> None:
        # 1) Configuración de Qdrant
        self.vector_config = VectorConfig()
        self.client = crear_cliente_qdrant()

        # 2) Modelo de embeddings (Gemini)
        self.embeddings_model = crear_modelo_embeddings()

        # 3) Cliente de Google Vision para OCR en imágenes
        self.vision_client = crear_cliente_vision()

    # ---------------------------------------------------------
    #  UTILIDAD: chunking simple
    # ---------------------------------------------------------
    def _chunkear_texto(
        self,
        texto: str,
        max_chars: int = 900,
        overlap: int = 150,
        # max_chunks: int = 200,
        max_chunks: int = 100, # limitar a 100 chunks por documento
    ) -> List[str]:
        """
        Divide un texto largo en chunks de tamaño aproximado max_chars,
        con solapamiento overlap. Limita a max_chunks por documento.
        """
        if not texto:
            return []

        chunks: List[str] = []
        inicio = 0
        longitud = len(texto)

        while inicio < longitud and len(chunks) < max_chunks:
            fin = min(inicio + max_chars, longitud)
            trozo = texto[inicio:fin].strip()
            if trozo:
                chunks.append(trozo)

            # Avance con solapamiento
            inicio = fin - overlap
            if inicio < 0:
                inicio = 0
            if inicio >= longitud:
                break

        if len(chunks) >= max_chunks:
            print("[WARN] Se alcanzó el máximo de chunks por documento.")

        return chunks

    # ---------------------------------------------------------
    #  LECTURA DE FUENTES (PDFs + IMÁGENES)
    # ---------------------------------------------------------
    def _leer_fuentes_desde_carpeta(
        self,
        carpeta: str = "data/ejemplos",
    ) -> List[Dict[str, Any]]:
        """
        Busca PDFs e imágenes en la carpeta y devuelve una lista de:
        [
            {
                "source_path": "ruta/al/archivo",
                "texto": "contenido textual extraído"
            },
            ...
        ]
        """
        print(f"[INGESTA] Buscando fuentes en: {carpeta}")

        patrones = [
            os.path.join(carpeta, "*.pdf"),
            os.path.join(carpeta, "*.png"),
            os.path.join(carpeta, "*.jpg"),
            os.path.join(carpeta, "*.jpeg"),
            os.path.join(carpeta, "*.txt"),
            os.path.join(carpeta, "*.md"),
        ]

        rutas: List[str] = []
        for patron in patrones:
            rutas.extend(glob.glob(patron))

        print(f"[INGESTA] Archivos encontrados: {rutas}")

        documentos: List[Dict[str, Any]] = []

        for ruta in rutas:
            ext = os.path.splitext(ruta)[1].lower()

            # ---------------- PDF ----------------
            if ext == ".pdf":
                print(f"[INGESTA] Leyendo PDF: {ruta}")
                try:
                    reader = PdfReader(ruta)
                    paginas_texto: List[str] = []
                    for page in reader.pages:
                        texto_pagina = page.extract_text() or ""
                        paginas_texto.append(texto_pagina)

                    contenido = "\n\n".join(paginas_texto).strip()
                    print(
                        f"[INGESTA]  -> Páginas: {len(reader.pages)} | "
                        f"Texto extraído: {len(contenido)} caracteres."
                    )

                    if not contenido:
                        # PDF sin texto legible (ej. escaneado sin OCR interno)
                        print(
                            "[WARN] PDF sin texto extraíble por pypdf. "
                            "Más adelante se podría manejar con Vision (OCR para PDF)."
                        )
                        continue

                    documentos.append(
                        {
                            "source_path": ruta,
                            "texto": contenido,
                        }
                    )
                except Exception as e:
                    print(f"[WARN] No se pudo leer el PDF {ruta}: {e}")

            # --------------- IMÁGENES ---------------
            elif ext in {".png", ".jpg", ".jpeg"}:
                print(f"[INGESTA] Leyendo imagen para OCR: {ruta}")
                try:
                    texto = extraer_texto_imagen_vision(
                        ruta_imagen=ruta,
                        client=self.vision_client,
                    ).strip()

                    print(
                        f"[INGESTA]  -> Texto OCR extraído: {len(texto)} caracteres."
                    )

                    if not texto:
                        print(
                            f"[WARN] La imagen {ruta} no produjo texto con Vision."
                        )
                        continue

                    documentos.append(
                        {
                            "source_path": ruta,
                            "texto": texto,
                        }
                    )
                except Exception as e:
                    print(f"[WARN] Error usando Vision OCR en {ruta}: {e}")

            # --------------- ARCHIVOS DE TEXTO (.txt, .md) ---------------
            elif ext in {".txt", ".md"}:
                print(f"[INGESTA] Leyendo archivo de texto: {ruta}")
                try:
                    with open(ruta, 'r', encoding='utf-8') as f:
                        contenido = f.read().strip()

                    print(f"[INGESTA]  -> Texto leído: {len(contenido)} caracteres.")

                    if not contenido:
                        print(f"[WARN] El archivo de texto {ruta} está vacío.")
                        continue

                    documentos.append(
                        {
                            "source_path": ruta,
                            "texto": contenido,
                        }
                    )
                except Exception as e:
                    print(f"[WARN] Error leyendo archivo de texto {ruta}: {e}")

            # --------------- OTROS ---------------
            else:
                print(f"[INGESTA] Tipo de archivo no soportado, se ignora: {ruta}")

        print(f"[INGESTA] Total fuentes con texto: {len(documentos)}")
        return documentos

    # ---------------------------------------------------------
    #  INGESTA PRINCIPAL
    # ---------------------------------------------------------
    def ingestar_documentos(self, carpeta: str = "data/ejemplos") -> int:
        """
        Lee PDFs e imágenes de la carpeta, extrae texto (pypdf / Vision),
        chunkéa, genera embeddings y hace upsert en Qdrant.

        Devuelve:
            número total de chunks insertados.
        """
        print("[INGESTA] Iniciando proceso de ingesta...")

        documentos = self._leer_fuentes_desde_carpeta(carpeta)

        if not documentos:
            print("[INFO] No se encontraron documentos/imagenes con texto para ingestar.")
            return 0

        puntos_a_insertar: List[PointStruct] = []
        total_chunks = 0

        for doc in documentos:
            source_path = doc["source_path"]
            texto = doc["texto"]

            #NUEVO
            # Determinar tipo de fuente y nombre de archivo para metadatos
            _, ext = os.path.splitext(source_path)
            ext = ext.lower()
            if ext in {".png", ".jpg", ".jpeg"}:
                tipo_fuente = "imagen"
            elif ext in {".txt", ".md"}:
                tipo_fuente = "texto"
            else:
                tipo_fuente = "pdf"

            nombre_archivo = os.path.basename(source_path)
            #NUEVO FIN

            print(f"[INGESTA] Chunking del documento: {source_path}")
            chunks = self._chunkear_texto(texto)
            print(f"[INGESTA]  -> Chunks generados: {len(chunks)}")

            if not chunks:
                continue

            # 1) Embeddings de todos los chunks de este documento
            print("[INGESTA]  -> Generando embeddings para los chunks...")
            vectores = self.embeddings_model.embed_documents(chunks)
            print("[INGESTA]  -> Embeddings generados.")

            # 2) Crear puntos para Qdrant
            for idx, (chunk_text, vector) in enumerate(zip(chunks, vectores)):
                punto_id = uuid.uuid4().int >> 64  # entero grande casi único

                # ANTERIOR PAYLOAD
                # payload = {
                #     "texto": chunk_text,
                #     "source_path": source_path,
                #     "chunk_index": idx,
                # }
                
                # NUEVO PAYLOAD CON TIPO DE FUENTE Y NOMBRE DE ARCHIVO
                payload = {
                    "texto": chunk_text,
                    "source_path": source_path,
                    "nombre_archivo": nombre_archivo,
                    "tipo_fuente": tipo_fuente,   # "pdf" o "imagen"
                    "chunk_index": idx,
                }


                puntos_a_insertar.append(
                    PointStruct(
                        id=punto_id,
                        vector=vector,
                        payload=payload,
                    )
                )

            total_chunks += len(chunks)
            print(f"[INGESTA]  -> Total de chunks acumulados: {total_chunks}")

        if not puntos_a_insertar:
            print("[INFO] No se generaron puntos para Qdrant.")
            return 0

        print(f"[INGESTA] Enviando {len(puntos_a_insertar)} puntos a Qdrant...")
        self.client.upsert(
            collection_name=self.vector_config.collection_name,
            points=puntos_a_insertar,
        )
        print(f"[OK] Se ingresaron {total_chunks} chunks en Qdrant.")
        return total_chunks
