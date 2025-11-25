"""
app.py

Interfaz principal del sistema.

- Expuesto vía FastAPI.
- Será el backend que consumirá:
  - un posible frontend Streamlit, o
  - una app en Next.js generada con v0 y desplegada en Vercel.
"""

from fastapi.middleware.cors import CORSMiddleware #<- NUEVO, para CORS

from pathlib import Path #<- NUEVO, para manejo de paths


# from fastapi import FastAPI
# from fastapi import FastAPI, UploadFile, File #<- NUEVO
from fastapi import FastAPI, UploadFile, File, HTTPException #<- NUEVO, HTTPException para manejo de errores
from pathlib import Path #<- NUEVO, para manejo de paths

from pydantic import BaseModel

import tempfile #<- NUEVO, para manejo de archivos temporales
from typing import List  # si no lo tenías ya importado arriba

#from src.agentes.agente_analisis import AgenteAnalisis
from src.agentes.agente_plan_repaso import AgentePlanRepaso #<- NUEVO
from src.agentes.agente_extraccion import AgenteExtraccion  # <- NUEVO
from src.agentes.agente_respuesta import AgenteRespuesta  # <- NUEVO
from src.ocr_vision import extraer_texto_imagen_vision # <- NUEVO

import os #<- NUEVO
import requests  # Para enviar webhooks

from datetime import date #<- NUEVO
from pydantic import BaseModel #<- NUEVO

# Carpeta base donde viven los PDFs / imágenes para ingesta y listado
BASE_DOCS_DIR = Path("data/ejemplos")


app = FastAPI(
    title="Mentor IA de Aprendizaje y Repaso",
    version="0.1.0",
    description="Prototipo multiagente con base de datos vectorial para apoyar el estudio.",
)

# Configuración de CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://mentor-ia-sistema.vercel.app",  # Origen de Vercel

    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#analisis_agent = AgenteAnalisis()
plan_agent = AgentePlanRepaso() #<- NUEVO
extraccion_agent = AgenteExtraccion() # <- NUEVO
respuesta_agent = AgenteRespuesta()  # <- NUEVO


class QueryRequest(BaseModel):
    pregunta: str


class PlanRepasoRequest(BaseModel):
    tema: str
    # fecha_inicio: date #<- NUEVO
    fecha_inicio: date | None = None #<- NUEVO
    email: str | None = None  # Para envío automático por email

# ---------------- LISTAR DOCUMENTOS ----------------

class DocumentoInfo(BaseModel):
    nombre: str
    size_bytes: int
    tipo: str

@app.get("/list-docs", response_model=List[DocumentoInfo])
def listar_documentos():
    """
    Devuelve la lista de PDFs e imágenes que están en data/ejemplos.
    Esto sirve para que el frontend muestre qué hay disponible para indexar.
    """
    try:
        docs_dir = "data/ejemplos"
        if not os.path.exists(docs_dir):
            print(f"Directorio {docs_dir} no existe")
            return []

        docs: List[DocumentoInfo] = []

        for item in os.listdir(docs_dir):
            # Saltar carpetas y ficheros raros (.DS_Store, etc.)
            if item.startswith("."):
                continue

            item_path = os.path.join(docs_dir, item)
            if not os.path.isfile(item_path):
                continue

            _, ext = os.path.splitext(item)
            ext = ext.lower()
            if ext not in {".pdf", ".png", ".jpg", ".jpeg", ".txt", ".md"}:
                continue

            try:
                size_bytes = os.path.getsize(item_path)
                docs.append(
                    DocumentoInfo(
                        nombre=item,
                        size_bytes=size_bytes,
                        tipo=ext.lstrip(".") or "desconocido",
                    )
                )
            except OSError as e:
                print(f"Error obteniendo tamaño de {item_path}: {e}")
                continue

        # Ordenar por nombre para que se vea bonito y estable
        docs.sort(key=lambda d: d.nombre.lower())

        return docs
    except Exception as e:
        print(f"Error in listar_documentos: {e}")
        import traceback
        traceback.print_exc()
        return []
# ---------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/plan-repaso")
def crear_plan_repaso(request: PlanRepasoRequest):
    # plan = analisis_agent.crear_plan_repaso(request.tema)
    # return plan
    return plan_agent.crear_plan(request.tema, request.fecha_inicio, request.email) #<- NUEVO


# FUNCIONAL - PERO SE CAMBIO POR UNA SALIDA MAS LIMPIA
# @app.post("/query")
# def hacer_pregunta(request: QueryRequest):
#     """
#     Endpoint que usa el AgenteRespuesta para hacer RAG sobre los documentos
#     previamente ingestados en Qdrant.
#     """
#     resultado = respuesta_agent.responder(request.pregunta)
#     return {
#         "pregunta": request.pregunta,
#         "respuesta": resultado["respuesta"],
#         "fuentes": resultado["fuentes"],
#     }

# NUEVO - RESPUESTA MAS DETALLADA
@app.post("/query")
def hacer_pregunta(request: QueryRequest):
    """
    Endpoint que usa el AgenteRespuesta para hacer RAG sobre los documentos
    previamente ingestados en Qdrant.
    """
    resultado = respuesta_agent.responder(request.pregunta)

    return {
        "pregunta": request.pregunta,
        "respuesta": resultado["respuesta"],
        "origen": resultado["origen"],
        "detalle_origen": resultado["detalle_origen"],
        "fuentes": resultado["fuentes"],
    }

 
# @app.post("/ingestar")  # <- NUEVO
# def ingestar_documentos():
#     """
#     Endpoint para lanzar la ingesta de documentos en data/ejemplos
#     hacia la base vectorial en Qdrant.
#     """
#     cantidad = extraccion_agent.ingestar_documentos()
#     return {"chunks_ingresados": cantidad}

# NUEVO - USANDO BASE_DOCS_DIR Para dejarlo explícito y consistente
@app.post("/ingestar")
def ingestar_documentos():
    """
    Endpoint para lanzar la ingesta de documentos en BASE_DOCS_DIR
    hacia la base vectorial en Qdrant.
    """
    cantidad = extraccion_agent.ingestar_documentos(str(BASE_DOCS_DIR))
    return {"chunks_ingresados": cantidad}


# ---------------- SUBIR PDF E INGESTAR ----------------
# @app.post("/upload-pdf")
# async def upload_pdf(file: UploadFile = File(...)):
#     """
#     Sube un PDF a data/ejemplos y lanza la ingesta sobre esa carpeta.
#     """

#     # Validación básica
#     filename = file.filename or ""
#     if not filename.lower().endswith(".pdf"):
#         raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

#     upload_dir = Path("data/ejemplos")
#     upload_dir.mkdir(parents=True, exist_ok=True)

#     dest_path = upload_dir / filename

#     # Guardar el PDF en disco
#     contenido = await file.read()
#     with dest_path.open("wb") as f:
#         f.write(contenido)

#     # Lanzar ingesta (escanea toda la carpeta data/ejemplos)
#     chunks_ingresados = extraccion_agent.ingestar_documentos(str(upload_dir))

#     return {
#         "filename": filename,
#         "chunks_ingresados": chunks_ingresados,
#     }

# NUEVO - SUBIR DOCUMENTO E INGESTAR USANDO BASE_DOCS_DIR
@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """
    Sube un documento (PDF, TXT, MD, imagen) a BASE_DOCS_DIR y lanza la ingesta sobre esa carpeta.
    """

    filename = file.filename or ""
    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    allowed_extensions = {".pdf", ".txt", ".md", ".png", ".jpg", ".jpeg"}
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no soportado. Extensiones permitidas: {', '.join(allowed_extensions)}"
        )

    # Usamos la carpeta base unificada
    upload_dir = BASE_DOCS_DIR
    upload_dir.mkdir(parents=True, exist_ok=True)

    dest_path = upload_dir / filename

    contenido = await file.read()
    with dest_path.open("wb") as f:
        f.write(contenido)

    # Lanzar ingesta (escanea toda la carpeta BASE_DOCS_DIR)
    chunks_ingresados = extraccion_agent.ingestar_documentos(str(upload_dir))

    return {
        "filename": filename,
        "chunks_ingresados": chunks_ingresados,
    }


# @app.post("/ocr-imagen", summary="Extraer texto de una imagen usando Google Vision") #<- NUEVO
# async def ocr_imagen(file: UploadFile = File(...)):
#     """
#     Recibe una imagen (jpg/png/webp) y extrae el texto usando Google Vision.
#     """
#     contenido = await file.read()
#     texto = extraer_texto_imagen_vision(contenido)

#     return {
#         "nombre_archivo": file.filename,
#         "texto_extraido": texto
#     }

@app.post("/ocr-imagen")
async def ocr_imagen(file: UploadFile = File(...)):
    # 1) Leemos los bytes del archivo subido
    contenido = await file.read()

    # 2) Creamos un archivo temporal con la misma extensión
    suffix = os.path.splitext(file.filename)[1] or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(contenido)
        tmp_path = tmp.name

    try:
        # 3) Llamamos a Vision usando la ruta temporal
        texto = extraer_texto_imagen_vision(ruta_imagen=tmp_path)
    finally:
        # 4) Borramos el archivo temporal
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    return {"texto": texto}


# # === Nuevo: listar documentos indexados ===

# BASE_DOCS_DIR = Path("data/ejemplos")

# @app.get("/documentos-indexados")
# def documentos_indexados():
#     """
#     Devuelve la lista de archivos (PDFs / imágenes) presentes en data/ejemplos.

#     Es solo informativo para el frontend: la ingesta real se sigue haciendo
#     con /ingestar.
#     """
#     docs = []

#     if not BASE_DOCS_DIR.exists():
#         return {"documentos": []}

#     for path in BASE_DOCS_DIR.glob("*"):
#         if not path.is_file():
#             continue

#         docs.append(
#             {
#                 "nombre": path.name,
#                 "ruta": str(path),
#                 "extension": path.suffix.lower(),
#             }
#         )

#     # Ordenar por nombre para que se vea bonito
#     docs.sort(key=lambda d: d["nombre"].lower())

#     return {"documentos": docs}

# === Nuevo: listar documentos indexados === Como ya movimos BASE_DOCS_DIR arriba, aquí solo asegúrate de quitar la redeclaración para que no esté dos veces.
#ya va bien, pero lo alineamos)
@app.get("/documentos-indexados")
def documentos_indexados():
    """
    Devuelve la lista de documentos que han sido indexados en Qdrant.
    Consulta la base de datos vectorial para obtener documentos únicos indexados.
    """
    try:
        from src.embeddings import crear_cliente_qdrant, VectorConfig

        # Conectar a Qdrant
        client = crear_cliente_qdrant()
        vector_config = VectorConfig()

        # Hacer scroll para obtener todos los puntos (con límite razonable)
        # Usamos scroll para obtener información de documentos indexados
        scroll_result = client.scroll(
            collection_name=vector_config.collection_name,
            limit=10000,  # Límite alto para obtener todos
            with_payload=True,
            with_vectors=False
        )

        # Extraer documentos únicos de los payloads
        documentos_unicos = {}
        total_chunks = 0

        for point in scroll_result[0]:  # scroll_result[0] contiene los puntos
            payload = point.payload or {}
            source_path = payload.get("source_path", "")
            nombre_archivo = payload.get("nombre_archivo", "")
            tipo_fuente = payload.get("tipo_fuente", "desconocido")

            if source_path and nombre_archivo:
                # Usar source_path como clave única
                if source_path not in documentos_unicos:
                    documentos_unicos[source_path] = {
                        "nombre": nombre_archivo,
                        "ruta": source_path,
                        "tipo": tipo_fuente,
                        "chunks": 0
                    }
                documentos_unicos[source_path]["chunks"] += 1
                total_chunks += 1

        # Convertir a lista y ordenar
        documentos = list(documentos_unicos.values())
        documentos.sort(key=lambda d: d["nombre"].lower())

        return {
            "documentos": documentos,
            "total_chunks": total_chunks,
            "total_documentos": len(documentos)
        }

    except Exception as e:
        print(f"Error consultando documentos indexados: {e}")
        return {
            "documentos": [],
            "total_chunks": 0,
            "total_documentos": 0
        }

# ---------------- WEBHOOK PARA ENVÍO DE EMAIL ----------------
@app.post("/webhook/plan-generado")
def webhook_plan_generado(data: dict):
    """
    Endpoint para que Make.com reciba notificaciones de planes generados.
    Espera un JSON con el plan completo y email destino.
    """
    # Aquí Make.com procesará el email
    # Por ahora, solo loggeamos
    print("Webhook recibido:", data)
    return {"status": "received"}
