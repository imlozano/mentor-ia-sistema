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

# ---------------- LISTAR DOCUMENTOS ----------------

class DocumentoInfo(BaseModel):
    nombre: str
    size_bytes: int
    tipo: str

@app.get("/docs", response_model=List[DocumentoInfo])
def listar_documentos():
    """
    Devuelve la lista de PDFs e imágenes que están en data/ejemplos.
    Esto sirve para que el frontend muestre qué hay indexado.
    """
    # FUNCIONAL - PERO SE CAMBIO POR UNA VERSIÓN MÁS COMPLETA ABAJO
    # carpeta = Path("data/ejemplos")
    # if not carpeta.exists():
    #     return []

    # docs: List[DocumentoInfo] = []
    # for ruta in carpeta.iterdir():
    #     if ruta.is_file() and ruta.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg"}:
    #         docs.append(
    #             DocumentoInfo(
    #                 nombre=ruta.name,
    #                 size_bytes=ruta.stat().st_size,
    #                 tipo=ruta.suffix.lower().lstrip("."),
    #             )
    #         )

    # return docs

    if not BASE_DOCS_DIR.exists():
        return []

    docs: List[DocumentoInfo] = []

    for ruta in BASE_DOCS_DIR.iterdir():
        # Saltar carpetas y ficheros raros (.DS_Store, etc.)
        if not ruta.is_file():
            continue
        if ruta.name.startswith("."):
            continue

        ext = ruta.suffix.lower()
        if ext not in {".pdf", ".png", ".jpg", ".jpeg"}:
            continue

        docs.append(
            DocumentoInfo(
                nombre=ruta.name,
                size_bytes=ruta.stat().st_size,
                tipo=ext.lstrip(".") or "desconocido",
            )
        )

    # Ordenar por nombre para que se vea bonito y estable
    docs.sort(key=lambda d: d.nombre.lower())

    return docs
# ---------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/plan-repaso")
def crear_plan_repaso(request: PlanRepasoRequest):
    # plan = analisis_agent.crear_plan_repaso(request.tema)
    # return plan
    return plan_agent.crear_plan(request.tema, request.fecha_inicio) #<- NUEVO


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

# NUEVO - SUBIR PDF E INGESTAR USANDO BASE_DOCS_DIR
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Sube un PDF a BASE_DOCS_DIR y lanza la ingesta sobre esa carpeta.
    """

    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

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
    Devuelve la lista de archivos (PDFs / imágenes) presentes en BASE_DOCS_DIR.
    Es solo informativo para el frontend.
    """
    if not BASE_DOCS_DIR.exists():
        return {"documentos": []}

    documentos = []

    for path in BASE_DOCS_DIR.glob("*"):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue

        documentos.append(
            {
                "nombre": path.name,
                "ruta": str(path),
                "extension": path.suffix.lower(),
            }
        )

    documentos.sort(key=lambda d: d["nombre"].lower())

    return {"documentos": documentos}
