"""
similitud.py

Funciones para realizar búsquedas por similitud en la base vectorial.
"""

# from typing import List, Tuple
# from typing import List
# from qdrant_client import QdrantClient
# from qdrant_client.models import ScoredPoint



# def buscar_similares(
#     client: QdrantClient,
#     collection_name: str,
#     query_vector: List[float],
#     top_k: int = 5,
# ) -> List[ScoredPoint]:
#     """
#     Realiza una búsqueda de los vectores más similares a query_vector
#     en la colección indicada.
#     """
#     results = client.search(
#         collection_name=collection_name,
#         query_vector=query_vector,
#         limit=top_k,
#     )
#     return results


# --- Código que no funciona porque llama a src.config que no existe. ---
# from qdrant_client import QdrantClient
# from qdrant_client import models  # por si luego queremos filtros

# from src.config import QDRANT_COLLECTION
# from src.qdrant_client_local import get_qdrant_client

# client: QdrantClient = get_qdrant_client()

# def buscar_similares(embedding, limit: int = 5):
#     """
#     Busca los puntos más similares en Qdrant usando la API moderna query_points.
#     embedding: lista de floats (vector de la pregunta)
#     limit: número máximo de resultados
#     """
#     response = client.query_points(
#         collection_name=QDRANT_COLLECTION,
#         query=embedding,          # antes: query_vector=...
#         limit=limit,
#         with_payload=True,        # queremos recuperar el texto guardado
#         with_vectors=False        # no necesitamos devolver los vectores
#     )

#     # response.points es una lista de ScoredPoint
#     puntos = []
#     for p in response.points:
#         payload = p.payload or {}
#         puntos.append({
#             "id": p.id,
#             "score": p.score,
#             # ajusta la clave según lo que uses en la ingesta:
#             "texto": payload.get("texto") or payload.get("content") or "",
#             "payload": payload,
#         })

#     return puntos

# src/similitud.py

from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint


def buscar_similares(
    client: QdrantClient,
    collection_name: str,
    query_vector: List[float],
    top_k: int = 5,
) -> List[ScoredPoint]:
    """
    Realiza una búsqueda de los vectores más similares a query_vector
    en la colección indicada usando la API moderna de Qdrant (query_points).
    """

    # En Qdrant moderno la forma recomendada de búsqueda es query_points
    response = client.query_points(
        collection_name=collection_name,
        query=query_vector,   # vector denso
        limit=top_k,
        with_payload=True,
        with_vectors=False,
    )

    # response es un QueryResponse; los resultados están en .points
    return response.points
