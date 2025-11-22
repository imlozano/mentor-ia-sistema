# """
# agente_respuesta.py

# Agente que responde preguntas concretas del usuario
# usando recuperación + generación (RAG).
# """

# import os
# from typing import Any, Dict, List

# from qdrant_client import QdrantClient # <- NUEVO
# from qdrant_client.models import ScoredPoint # <- NUEVO

# from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI

# from src.embeddings import (
#     crear_cliente_qdrant,
#     crear_modelo_embeddings,
#     VectorConfig,
# )
# from src.similitud import buscar_similares

# load_dotenv()


# class AgenteRespuesta:
#     def __init__(self) -> None:
#         # Cliente y configuración de Qdrant
#         # self.client = crear_cliente_qdrant()
#         self.vector_config = VectorConfig()
#         self.qdrant_client: QdrantClient = crear_cliente_qdrant(self.vector_config) # <- NUEVO



#         # Modelo de embeddings (Gemini)
#         self.embeddings_model = crear_modelo_embeddings()

#         # Modelo de lenguaje (Gemini como chat)
#         api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
#         if not api_key:
#             raise ValueError("Falta GOOGLE_API_KEY o GEMINI_API_KEY en el archivo .env")

#         # Puedes cambiar el modelo si quieres (ej. "gemini-1.5-pro")
#         self.llm = ChatGoogleGenerativeAI(
#             model="gemini-1.5-flash",
#             google_api_key=api_key,
#             temperature=0.2,
#         )

#     def _recuperar_contexto(self, pregunta: str, top_k: int = 5) -> List[Dict[str, Any]]:
#         """
#         Genera el embedding de la pregunta y recupera los chunks más similares
#         desde Qdrant.
#         """
#         # query_vector = self.embeddings_model.embed_query(pregunta)

#          # 1) Embedding de la pregunta
#         vector_pregunta: List[float] = self.embeddings_model.embed_query(pregunta)

#          # 2) Llamar a buscar_similares con client + nombre de colección
#         results = buscar_similares(
#             client=self.qdrant_client,
#             collection_name=self.vector_config.collection_name,
#             query_vector=vector_pregunta,
#             top_k=5,
#         )

#         # results = buscar_similares(
#         #     client=self.client,
#         #     collection_name=self.vector_config.collection_name,
#         #     query_vector=query_vector,
#         #     top_k=top_k,
#         # )

#         # contexto: List[Dict[str, Any]] = []
#         # for point in results:
#         #     payload = point.payload or {}
#         #     contexto.append(
#         #         {
#         #             "texto": payload.get("text", ""),
#         #             "source_path": payload.get("source_path"),
#         #             "chunk_index": payload.get("chunk_index"),
#         #             "score": point.score,
#         #         }
#         #     )

#         # return contexto

#         # 3) Armar el contexto concatenando los textos recuperados
#         textos = []
#         for punto in results:
#             payload = punto.payload or {}
#             texto_chunk = payload.get("texto", "")
#             if texto_chunk:
#                 textos.append(texto_chunk)

#         contexto = "\n\n".join(textos)
#         return contexto

#     def _construir_prompt(self, pregunta: str, contexto: List[Dict[str, Any]]) -> str:
#         """
#         Construye el prompt para el LLM usando los chunks recuperados.
#         """
#         partes_contexto = []
#         for i, c in enumerate(contexto, start=1):
#             partes_contexto.append(f"[Fragmento {i}]\n{c['texto']}\n")

#         contexto_texto = "\n\n".join(partes_contexto) if partes_contexto else "No hay contexto disponible."

#         prompt = f"""
# Eres un asistente de estudio que responde preguntas de manera clara y breve,
# basándote SOLO en el contexto proporcionado.

# CONTEXTO:
# {contexto_texto}

# PREGUNTA DEL ESTUDIANTE:
# {pregunta}

# INSTRUCCIONES:
# - Si el contexto es suficiente, responde de forma directa y clara.
# - Si el contexto NO es suficiente, dilo explícitamente.
# - No inventes información que no esté respaldada por el contexto.
# - Puedes estructurar la respuesta con viñetas si ayuda a la claridad.
# """
#         return prompt

#     def responder(self, pregunta: str) -> Dict[str, Any]:
#         """
#         Devuelve un diccionario con:
#         {
#             "respuesta": "...",
#             "fuentes": [...]
#         }
#         """
#         contexto = self._recuperar_contexto(pregunta)

#         prompt = self._construir_prompt(pregunta, contexto)

#         # Llamamos al modelo de lenguaje
#         respuesta_llm = self.llm.invoke(prompt)
#         texto_respuesta = respuesta_llm.content if hasattr(respuesta_llm, "content") else str(respuesta_llm)

#         return {
#             "respuesta": texto_respuesta,
#             "fuentes": contexto,
#         }


"""
agente_respuesta.py

Agente que responde preguntas concretas del usuario
usando recuperación + generación (RAG).
"""

import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from src.embeddings import (
    crear_cliente_qdrant,
    crear_modelo_embeddings,
    VectorConfig,
)
from src.similitud import buscar_similares

load_dotenv()


class AgenteRespuesta:
    def __init__(self) -> None:
        # 1) Configuración de Qdrant
        self.vector_config = VectorConfig()
        self.client = crear_cliente_qdrant()  # <- SIN argumentos

        # 2) Modelo de embeddings (Gemini)
        self.embeddings_model = crear_modelo_embeddings()

        # 3) Modelo de lenguaje (Gemini como chat)
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Falta GOOGLE_API_KEY o GEMINI_API_KEY en el archivo .env")

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest", # <-nuevo
            google_api_key=api_key,
            temperature=0.2,
        )

    def _recuperar_contexto(
        self,
        pregunta: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Genera el embedding de la pregunta y recupera los chunks más similares
        desde Qdrant, devolviendo una lista de diccionarios con metadatos.
        """

        # 1) Embedding de la pregunta
        query_vector: List[float] = self.embeddings_model.embed_query(pregunta)

        # 2) Buscar puntos similares en Qdrant
        puntos = buscar_similares(
            client=self.client,
            collection_name=self.vector_config.collection_name,
            query_vector=query_vector,
            top_k=top_k,
        )

        # 3) Convertir resultados en estructura amigable
        contexto: List[Dict[str, Any]] = []
        for p in puntos:
            payload = p.payload or {}

            # Ajusta estas claves según lo que uses en la ingesta.
            # Si en tu ingesta guardaste el texto como "text", se toma de ahí.
            texto = (
                payload.get("text")
                or payload.get("texto")
                or payload.get("content")
                or ""
            )

            contexto.append(
                {
                    "texto": texto,
                    "source_path": payload.get("source_path"),
                    "chunk_index": payload.get("chunk_index"),
                    "score": p.score,
                }
            )

        return contexto

    def _construir_prompt(
        self,
        pregunta: str,
        contexto: List[Dict[str, Any]],
    ) -> str:
        """
        Construye el prompt para el LLM usando los chunks recuperados.
        """
        partes_contexto: List[str] = []
        for i, c in enumerate(contexto, start=1):
            texto = c.get("texto", "")
            if texto:
                partes_contexto.append(f"[Fragmento {i}]\n{texto}\n")

        contexto_texto = (
            "\n\n".join(partes_contexto)
            if partes_contexto
            else "No hay contexto disponible."
        )

        prompt = f"""
Eres un asistente de estudio que responde preguntas de manera clara y breve,
basándote SOLO en el contexto proporcionado.

CONTEXTO:
{contexto_texto}

PREGUNTA DEL ESTUDIANTE:
{pregunta}

INSTRUCCIONES:
- Si el contexto es suficiente, responde de forma directa y clara.
- Si el contexto NO es suficiente, dilo explícitamente.
- No inventes información que no esté respaldada por el contexto.
- Puedes estructurar la respuesta con viñetas si ayuda a la claridad.
"""
        return prompt

    def responder(self, pregunta: str) -> Dict[str, Any]:
        """
        Devuelve un diccionario con:
        {
            "respuesta": "...",
            "fuentes": [...]
        }
        """
        contexto = self._recuperar_contexto(pregunta)
        prompt = self._construir_prompt(pregunta, contexto)

        respuesta_llm = self.llm.invoke(prompt)
        texto_respuesta = (
            respuesta_llm.content
            if hasattr(respuesta_llm, "content")
            else str(respuesta_llm)
        )

        return {
            "respuesta": texto_respuesta,
            "fuentes": contexto,
        }
