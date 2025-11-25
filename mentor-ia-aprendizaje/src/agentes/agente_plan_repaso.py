"""
agente_plan_repaso.py

Agente encargado de:
- Crear planes de repaso (D+1, D+7, D+14, D+30).
- Intentar usar contexto de PDFs indexados en Qdrant.
- Si no hay contexto útil en PDFs, hacer fallback al conocimiento general del modelo.
"""

import os
import requests
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from src.embeddings import (
    VectorConfig,
    crear_cliente_qdrant,
    crear_modelo_embeddings,
)
from src.similitud import buscar_similares

load_dotenv()
print(f"DEBUG: Current working directory: {os.getcwd()}")
print(f"DEBUG: .env file exists: {os.path.exists('.env')}")


class AgentePlanRepaso:
    def __init__(self) -> None:
        # 1) Configuración de Qdrant (igual que en AgenteRespuesta)
        self.vector_config = VectorConfig()
        self.client = crear_cliente_qdrant()

        # 2) Modelo de embeddings (Gemini, mismo que usas para indexar)
        self.embeddings_model = crear_modelo_embeddings()

        # 3) Modelo de lenguaje (Gemini flash)
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Falta GOOGLE_API_KEY o GEMINI_API_KEY en el archivo .env")

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            google_api_key=api_key,
            temperature=0.7,
        )

    # ---------------------------------------------------------
    #  MÉTODO PRIVADO: buscar contexto relevante en Qdrant
    # ---------------------------------------------------------
    # def _buscar_contexto_en_pdfs(
    #     self,
    #     tema: str,
    #     top_k: int = 5,
    #     umbral_score: float = 0.35,
    # ) -> Dict[str, Any]:
    #     """
    #     Busca en Qdrant fragmentos relevantes sobre el tema.

    #     Devuelve:
    #     {
    #         "uso_pdf": bool,
    #         "fragmentos": List[str],    # texto plano para el prompt
    #         "fuentes": List[Dict[str, Any]],  # metadatos de los puntos
    #     }
    #     """

    #     # 1) Embedding del tema
    #     query_vector: List[float] = self.embeddings_model.embed_query(tema)

    #     # 2) Recuperar puntos similares usando tu helper buscar_similares
    #     puntos = buscar_similares(
    #         client=self.client,
    #         collection_name=self.vector_config.collection_name,
    #         query_vector=query_vector,
    #         top_k=top_k,
    #     )

    #     if not puntos:
    #         return {
    #             "uso_pdf": False,
    #             "fragmentos": [],
    #             "fuentes": [],
    #         }

    #     fragmentos: List[str] = []
    #     fuentes: List[Dict[str, Any]] = []

    #     for p in puntos:
    #         payload = p.payload or {}

    #         texto = (
    #             payload.get("text")
    #             or payload.get("texto")
    #             or payload.get("content")
    #             or ""
    #         )

    #         if texto:
    #             fragmentos.append(texto)

    #         fuentes.append(
    #             {
    #                 "texto": texto,
    #                 "source_path": payload.get("source_path"),
    #                 "chunk_index": payload.get("chunk_index"),
    #                 "score": p.score,
    #             }
    #         )

    #     if not fragmentos:
    #         # Hay puntos pero sin texto útil
    #         return {
    #             "uso_pdf": False,
    #             "fragmentos": [],
    #             "fuentes": fuentes,
    #         }

    #     # 3) Opcional: filtrar por score mínimo
    #     fragmentos_filtrados: List[str] = []
    #     for texto, punto in zip(fragmentos, puntos):
    #         if punto.score is None or punto.score >= umbral_score:
    #             fragmentos_filtrados.append(texto)

    #     if not fragmentos_filtrados:
    #         fragmentos_filtrados = fragmentos

    #     return {
    #         "uso_pdf": True,
    #         "fragmentos": fragmentos_filtrados,
    #         "fuentes": fuentes,
    #     }

    def _buscar_contexto_en_pdfs(
        self,
        tema: str,
        top_k: int = 5,
        umbral_score: float = 0.45,
        min_score_para_usar_pdf: float = 0.60,
    ) -> Dict[str, Any]:
        """
        Busca en Qdrant fragmentos relevantes sobre el tema.

        Devuelve:
        {
            "uso_pdf": bool,
            "fragmentos": List[str],      # texto plano para el prompt (solo si uso_pdf=True)
            "fuentes": List[Dict[str, Any]],
        }

        Lógica importante:
        - Nunca fuerza uso_pdf=True solo porque haya resultados.
        - Solo usa PDFs si:
          * hay fragmentos con score >= umbral_score
          * el mejor score >= min_score_para_usar_pdf
          * y alguna palabra del tema aparece en el texto de los fragmentos
        """

        # 1) Embedding del tema
        query_vector: List[float] = self.embeddings_model.embed_query(tema)

        # 2) Recuperar puntos similares
        puntos = buscar_similares(
            client=self.client,
            collection_name=self.vector_config.collection_name,
            query_vector=query_vector,
            top_k=top_k,
        )

        if not puntos:
            return {
                "uso_pdf": False,
                "fragmentos": [],
                "fuentes": [],
            }

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
            # Hay puntos pero sin texto útil
            return {
                "uso_pdf": False,
                "fragmentos": [],
                "fuentes": fuentes,
            }

        # 3) Filtrar por score mínimo para considerar un fragmento "usable"
        fragmentos_filtrados: List[str] = []
        for texto, score in zip(fragmentos, scores):
            if score >= umbral_score:
                fragmentos_filtrados.append(texto)

        if not fragmentos_filtrados:
            # No hay nada suficientemente parecido → no usamos PDFs
            return {
                "uso_pdf": False,
                "fragmentos": [],
                "fuentes": fuentes,
            }

        # 4) Comprobar si el mejor score es suficientemente alto
        max_score = max(scores) if scores else 0.0
        if max_score < min_score_para_usar_pdf:
            # Hay cierto parecido pero flojo → mejor usar conocimiento general
            return {
                "uso_pdf": False,
                "fragmentos": [],
                "fuentes": fuentes,
            }

        # 5) Comprobar coincidencia léxica con el tema (palabras clave)
        import re

        tema_tokens = [
            t.lower()
            for t in re.split(r"\W+", tema)
            if len(t) > 2
        ]  # quitamos tokens muy cortos

        texto_concatenado = "\n\n".join(fragmentos_filtrados).lower()
        coincidencias = sum(
            1 for token in tema_tokens if token in texto_concatenado
        )

        if coincidencias == 0:
            # Ninguna palabra del tema aparece en los fragmentos → probablemente ruido
            return {
                "uso_pdf": False,
                "fragmentos": [],
                "fuentes": fuentes,
            }

        # Si llegamos aquí, consideramos que SÍ tiene sentido usar PDFs
        return {
            "uso_pdf": True,
            "fragmentos": fragmentos_filtrados,
            "fuentes": fuentes,
        }


    # ---------------------------------------------------------
    #  MÉTODO PÚBLICO: crear plan de repaso híbrido
    # ---------------------------------------------------------
    def crear_plan(
        self,
        tema: str,
        fecha_inicio: Optional[date] = None,
        email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Crea un plan de repaso con D+1, D+7, D+14, D+30.

        - Si encuentra contexto en Qdrant → usa PDFs.
        - Si no encuentra contexto útil → usa conocimiento general del modelo.

        Devuelve un dict con:
        {
            "tema": str,
            "fecha_inicio": "YYYY-MM-DD",
            "origen": "pdf" | "modelo",
            "detalle_origen": str,
            "fuentes": [...],
            "sesiones": [
                {
                    "tipo": "D+1",
                    "fecha": "YYYY-MM-DD",
                    "descripcion": "Markdown..."
                },
                ...
            ]
        }
        """
        if fecha_inicio is None:
            fecha_inicio = date.today()

        # 1) Intentar recuperar contexto desde PDFs (Qdrant)
        contexto = self._buscar_contexto_en_pdfs(tema)
        uso_pdf = contexto["uso_pdf"]
        fragmentos = contexto["fragmentos"]

        if uso_pdf:
            origen = "pdf"
            detalle_origen = (
                "El plan se generó utilizando contenido de los PDFs "
                "indexados en Qdrant relacionados con este tema."
            )
            # Concatenamos algunos fragmentos para el prompt (sin exagerar)
            contexto_texto = "\n\n".join(fragmentos[:5])
        else:
            origen = "modelo"
            detalle_origen = (
                "No se encontró contenido relevante sobre este tema en los PDFs "
                "cargados. El plan se generó con base en el conocimiento general "
                "del modelo."
            )
            contexto_texto = ""

        sesiones_config = [
            ("D+1", 1),
            ("D+7", 7),
            ("D+14", 14),
            ("D+30", 30),
        ]

        sesiones: List[Dict[str, Any]] = []

        # 2) Generar cada sesión de repaso
        for tipo, dias in sesiones_config:
            fecha_sesion = fecha_inicio + timedelta(days=dias)

            if uso_pdf:
                prompt = f"""
Eres un mentor de estudio especializado en aprendizaje efectivo basado en materiales de referencia.

TEMA: {tema}
TIPO DE SESIÓN: {tipo} (repetición espaciada, día +{dias} desde el inicio).
FECHA DE LA SESIÓN: {fecha_sesion.isoformat()}.

A continuación tienes fragmentos del material de estudio (extraídos de PDFs):

<contexto_pdf>
{contexto_texto}
</contexto_pdf>

Usa EXCLUSIVAMENTE este contexto para diseñar una sesión de repaso breve.

Responde en el siguiente formato en Markdown:

Objetivo: [una sola frase clara y concreta]
Tiempo estimado: [X minutos]
Actividades:
- [actividad 1 muy específica, ligada al contexto]
- [actividad 2 muy específica, ligada al contexto]
- [actividad 3 muy específica, ligada al contexto]
"""
            else:
                prompt = f"""
Eres un mentor de estudio.

No tienes acceso a PDFs ni material personalizado para este tema.
Debes generar un plan de repaso con base en tu conocimiento general.

TEMA: {tema}
TIPO DE SESIÓN: {tipo} (repetición espaciada, día +{dias} desde el inicio).
FECHA DE LA SESIÓN: {fecha_sesion.isoformat()}.

Responde en el siguiente formato en Markdown:

Objetivo: [una sola frase clara y concreta]
Tiempo estimado: [X minutos]
Actividades:
- [actividad 1 muy específica]
- [actividad 2 muy específica]
- [actividad 3 muy específica]
"""

            respuesta_llm = self.llm.invoke(prompt)
            descripcion = (
                respuesta_llm.content
                if hasattr(respuesta_llm, "content")
                else str(respuesta_llm)
            )

            sesiones.append(
                {
                    "tipo": tipo,
                    "fecha": fecha_sesion.isoformat(),
                    "descripcion": descripcion,
                }
            )

        # 3) Preparar respuesta final
        plan_response = {
            "tema": tema,
            "fecha_inicio": fecha_inicio.isoformat(),
            "origen": origen,               # "pdf" o "modelo"
            "detalle_origen": detalle_origen,
            "fuentes": contexto["fuentes"] if uso_pdf else [],  # útil para debug / UI / auditoría
            "sesiones": sesiones,
        }

        # 4) Si se proporcionó email, enviar webhook para automatización
        if email:
            webhook_url = os.getenv("MAKE_WEBHOOK_URL")  # URL del webhook de Make.com
            print(f"DEBUG: MAKE_WEBHOOK_URL = {webhook_url}")  # Debug
            if webhook_url:
                try:
                    webhook_data = {
                        "email": email,
                        **plan_response
                    }
                    print(f"DEBUG: Enviando webhook a: {webhook_url}")
                    print(f"DEBUG: Datos del webhook: {webhook_data}")
                    response = requests.post(webhook_url, json=webhook_data, timeout=5)
                    print(f"Webhook enviado a Make.com: {response.status_code}")
                    if response.status_code != 200:
                        print(f"Respuesta de Make.com: {response.text}")
                except Exception as e:
                    print(f"Error enviando webhook: {e}")
            else:
                print("MAKE_WEBHOOK_URL no configurada, omitiendo envío de webhook")

        return plan_response

