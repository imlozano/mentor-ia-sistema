"""
embeddings.py

Generación de embeddings con Gemini y conexión con la base de datos vectorial (Qdrant).
"""

import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Cargar variables de entorno desde .env
load_dotenv()


@dataclass
class VectorConfig:
    collection_name: str = os.getenv("QDRANT_COLLECTION", "mentor_ia_aprendizaje")
    vector_size: int = 768  # tamaño típico para muchos modelos; Gemini ajusta internamente
    distance: Distance = Distance.COSINE


def crear_cliente_qdrant() -> QdrantClient:
    """
    Crea un cliente de Qdrant apuntando a Qdrant Cloud (o local, si cambias la URL).

    Usa:
    - QDRANT_URL
    - QDRANT_API_KEY
    desde .env
    """
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")

    if not url:
        raise ValueError("Falta QDRANT_URL en el archivo .env")

    client = QdrantClient(url=url, api_key=api_key)
    return client


def asegurar_coleccion(
    client: QdrantClient,
    config: VectorConfig,
) -> None:
    """
    Crea la colección en Qdrant si no existe.
    """
    existing = [c.name for c in client.get_collections().collections]
    if config.collection_name in existing:
        return

    client.recreate_collection(
        collection_name=config.collection_name,
        vectors_config=VectorParams(
            size=config.vector_size,
            distance=config.distance,
        ),
    )


def crear_modelo_embeddings() -> GoogleGenerativeAIEmbeddings:
    """
    Crea el modelo de embeddings usando Gemini vía LangChain.

    Usa GOOGLE_API_KEY desde .env (nombre esperado por langchain-google-genai).
    """
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Falta GOOGLE_API_KEY o GEMINI_API_KEY en el archivo .env")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=api_key,  # <-- clave explícita, así NO intenta ADC
    )
    return embeddings



def generar_embeddings(
    texts: List[str],
    embeddings_model: GoogleGenerativeAIEmbeddings,
) -> List[List[float]]:
    """
    Genera embeddings para una lista de textos usando el modelo indicado.
    """
    return embeddings_model.embed_documents(texts)
