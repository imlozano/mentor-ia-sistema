"""
agente_respuesta.py

Agente que responde preguntas concretas del usuario
usando recuperación inteligente + generación (RAG híbrido).
"""

import os
import re
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
        # Qdrant
        self.vector_config = VectorConfig()
        self.client = crear_cliente_qdrant()

        # Embeddings
        self.embeddings_model = crear_modelo_embeddings()

        # LLM
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Falta GOOGLE_API_KEY o GEMINI_API_KEY en el archivo .env")

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            google_api_key=api_key,
            temperature=0.25,
        )

    # ---------------------------------------------------------
    #     BÚSQUEDA INTELIGENTE EN PDF (mismo criterio que PlanRepaso)
    # ---------------------------------------------------------
    def _buscar_contexto_pdf(
        self,
        pregunta: str,
        top_k: int = 5,
        umbral_score: float = 0.45,
        min_score_para_usar_pdf: float = 0.60,
    ) -> Dict[str, Any]:

        query_vector: List[float] = self.embeddings_model.embed_query(pregunta)

        puntos = buscar_similares(
            client=self.client,
            collection_name=self.vector_config.collection_name,
            query_vector=query_vector,
            top_k=top_k,
        )

        if not puntos:
            return {"uso_pdf": False, "fragmentos": [], "fuentes": []}

        fragmentos: List[str] = []
        fuentes: List[Dict[str, Any]] = []
        scores: List[float] = []

        for p in puntos:
            payload = p.payload or {}

            texto = (
                payload.get("text")
                or payload.get("texto")
                or payload.get("content")
                or ""
            )

            if texto:
                fragmentos.append(texto)

            fuentes.append(
                {
                    "texto": texto,
                    "source_path": payload.get("source_path"),
                    "chunk_index": payload.get("chunk_index"),
                    "score": p.score,
                }
            )

            scores.append(p.score if p.score is not None else 0.0)

        if not fragmentos:
            return {"uso_pdf": False, "fragmentos": [], "fuentes": fuentes}

        # 1) Filtrar por score
        fragmentos_filtrados = [
            f for f, s in zip(fragmentos, scores) if s >= umbral_score
        ]

        if not fragmentos_filtrados:
            return {"uso_pdf": False, "fragmentos": [], "fuentes": fuentes}

        # 2) Validar score máximo
        max_score = max(scores)
        if max_score < min_score_para_usar_pdf:
            return {"uso_pdf": False, "fragmentos": [], "fuentes": fuentes}

        # 3) Coincidencia léxica (misma técnica usada en PlanRepaso)
        tokens = [
            t.lower()
            for t in re.split(r"\W+", pregunta)
            if len(t) > 2
        ]

        texto_total = "\n".join(fragmentos_filtrados).lower()
        coincidencias = sum(1 for t in tokens if t in texto_total)

        if coincidencias == 0:
            return {"uso_pdf": False, "fragmentos": [], "fuentes": fuentes}

        return {
            "uso_pdf": True,
            "fragmentos": fragmentos_filtrados,
            "fuentes": fuentes,
        }
        
    # ---------------------------------------------------------
    # Formateo "bonito" de las fuentes (PDF / imagen)
    # ---------------------------------------------------------
    def _formatear_fuente(self, fuente: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recibe un diccionario fuente (tal como viene de Qdrant)
        y devuelve un diccionario listo para el frontend.
        """
        path = (fuente.get("source_path") or "").strip()
        nombre = os.path.basename(path) if path else None

        # Detectar tipo de archivo por extensión
        tipo = "desconocido"
        if path:
            ext = os.path.splitext(path)[1].lower()
            if ext == ".pdf":
                tipo = "pdf"
            elif ext in {".png", ".jpg", ".jpeg", ".webp"}:
                tipo = "imagen"

        # Texto recortado para no mandar todo el chunk
        texto_resumen = (fuente.get("texto") or "").strip()
        if len(texto_resumen) > 300:
            texto_resumen = texto_resumen[:300] + "..."

        return {
            "tipo": tipo,                 # "pdf" | "imagen" | "desconocido"
            "archivo": nombre,            # nombre del archivo (sin ruta)
            "source_path": path,          # ruta completa (por si la necesitas)
            "chunk_index": fuente.get("chunk_index"),
            "score": fuente.get("score"),
            "texto": texto_resumen,       # resumen del fragmento
        }

    # ---------------------------------------------------------
    # Construcción de prompts
    # ---------------------------------------------------------
    def _prompt_con_contexto(self, pregunta: str, contexto: str) -> str:
        return f"""
Eres un asistente de estudio.
Responde usando EXCLUSIVAMENTE el siguiente material:

<contexto_pdf>
{contexto}
</contexto_pdf>

PREGUNTA:
{pregunta}

Instrucciones:
- Responde solo con información del contexto.
- Si la respuesta está explícitamente en el texto, úsala.
- No inventes nada fuera del contenido.
"""

    def _prompt_sin_contexto(self, pregunta: str) -> str:
        return f"""
Eres un asistente de estudio.
No tienes acceso a PDFs relevantes para esta pregunta.

Responde usando tu conocimiento general, de forma clara y breve.

PREGUNTA:
{pregunta}
"""

    # ---------------------------------------------------------
    # RESPUESTA PRINCIPAL (HÍBRIDA)
    # ---------------------------------------------------------
    def responder(self, pregunta: str) -> Dict[str, Any]:

        contexto = self._buscar_contexto_pdf(pregunta)
        uso_pdf = contexto["uso_pdf"]

        if uso_pdf:
            # Creamos prompt RAG
            contexto_texto = "\n\n".join(contexto["fragmentos"][:5])
            prompt = self._prompt_con_contexto(pregunta, contexto_texto)

            # ANTES
            # origen = "pdf"
            # detalle = "Se usaron fragmentos relevantes de los PDFs indexados en Qdrant."

            #DESPUES - MÁS DETALLE
            origen = "rag"
            detalle = "Se usaron fragmentos relevantes recuperados desde embeddings (PDFs e imágenes con OCR)."


        else:
            # Prompt sin PDFs
            prompt = self._prompt_sin_contexto(pregunta)

            origen = "modelo"
            detalle = "No se encontró contexto relevante en PDFs. La respuesta proviene del conocimiento general del modelo."

        # FUNCIONA - PERO LO CAMBIAMOS POR EL DE ABAJO
        # respuesta_llm = self.llm.invoke(prompt)
        # texto_respuesta = (
        #     respuesta_llm.content
        #     if hasattr(respuesta_llm, "content")
        #     else str(respuesta_llm)
        # )

        # return {
        #     "origen": origen,
        #     "detalle_origen": detalle,
        #     "respuesta": texto_respuesta,
        #     "fuentes": contexto["fuentes"] if uso_pdf else [],
        # }

        respuesta_llm = self.llm.invoke(prompt)
        

        # -> DESDE ACA DEVUELVE EN OTRO FORMATO
        # texto_respuesta = (
        #     respuesta_llm.content
        #     if hasattr(respuesta_llm, "content")
        #     else str(respuesta_llm)
        # )

        # # Fuentes formateadas para el frontend
        # fuentes_crudas = contexto["fuentes"] if uso_pdf else []
        # fuentes_formateadas = [
        #     self._formatear_fuente(f) for f in fuentes_crudas
        # ]
        # HASTA ACA DEVUELVE EN OTRO FORMATO <-

        # 🔽 NORMALIZAR SIEMPRE A STRING
        contenido = getattr(respuesta_llm, "content", respuesta_llm)

        if isinstance(contenido, list):
            # LangChain + Gemini suelen devolver lista de partes { "type": "text", "text": "..."}
            partes_texto = []
            for part in contenido:
                if isinstance(part, dict) and "text" in part:
                    partes_texto.append(part["text"])
                elif hasattr(part, "text"):
                    partes_texto.append(part.text)
                else:
                    partes_texto.append(str(part))
            texto_respuesta = "".join(partes_texto).strip()
        else:
            texto_respuesta = str(contenido).strip()
        # 🔼 HASTA AQUÍ CAMBIO

        return {
            "origen": origen,
            "detalle_origen": detalle,
            "respuesta": texto_respuesta,
            "fuentes": contexto["fuentes"] if uso_pdf else [], #<- NUEVO
            # "fuentes": fuentes_formateadas,
        }

