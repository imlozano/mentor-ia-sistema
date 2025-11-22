"""
agente_plan_repaso.py

Agente encargado de:
- Generar resúmenes.
- Crear notas efectivas (idea principal, explicación, ejemplo).
- Crear planes de repaso según la metodología (D+1, D+7, D+14, D+30).
"""

from datetime import date, timedelta
from typing import Any, Dict, List

import os #<- NUEVO
from langchain_google_genai import ChatGoogleGenerativeAI #<- NUEVO
from dotenv import load_dotenv #<- NUEVO

load_dotenv() #<- NUEVO

# class AgenteAnalisis:
#     def generar_resumen(self, tema: str) -> str:
#         """
#         Genera un resumen del tema usando RAG.
#         Más adelante: LangChain + RAG sobre Qdrant.
#         """
#         raise NotImplementedError

#     def generar_notas_efectivas(self, tema: str) -> Dict[str, str]:
#         """
#         Devuelve una estructura tipo:
#         {
#             "idea_principal": "...",
#             "explicacion": "...",
#             "ejemplo": "..."
#         }
#         """
#         raise NotImplementedError

#     def crear_plan_repaso(self, tema: str, fecha_inicio: date | None = None) -> Dict[str, Any]:
#         """
#         Calcula las fechas de repaso siguiendo el método:
#         D+1, D+7, D+14, D+30.
#         """
#         if fecha_inicio is None:
#             fecha_inicio = date.today()

#         sesiones = [
#             {"offset_dias": 1, "tipo": "D+1"},
#             {"offset_dias": 7, "tipo": "D+7"},
#             {"offset_dias": 14, "tipo": "D+14"},
#             {"offset_dias": 30, "tipo": "D+30"},
#         ]

#         plan = {
#             "tema": tema,
#             "fecha_inicio": str(fecha_inicio),
#             "sesiones": [],
#         }

#         for ses in sesiones:
#             fecha_sesion = fecha_inicio + timedelta(days=ses["offset_dias"])
#             plan["sesiones"].append(
#                 {
#                     "tipo": ses["tipo"],
#                     "fecha": str(fecha_sesion),
#                 }
#             )

#         return plan

class AgentePlanRepaso:
    def __init__(self) -> None:
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Falta GOOGLE_API_KEY o GEMINI_API_KEY en el .env")

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",      # aquí sí puedes dejarlo a 0.7
            temperature=0.7,
            google_api_key=api_key,
        )

    def crear_plan(self, tema: str, fecha_inicio: date) -> Dict[str, Any]:
        sesiones_config = [
            ("D+1", 1),
            ("D+7", 7),
            ("D+14", 14),
            ("D+30", 30),
        ]

        sesiones: List[Dict[str, Any]] = []

        for tipo, dias in sesiones_config:
            fecha = fecha_inicio + timedelta(days=dias)

            prompt = f"""
Eres un mentor de estudio.
Tema: {tema}
Tipo de sesión: {tipo} (repetición espaciada, día +{dias} desde el inicio).
Fecha de la sesión: {fecha.isoformat()}.

Diseña una sesión de estudio breve con:
- Un objetivo en UNA sola frase.
- 3 actividades concretas (bullet points).
- Tiempo estimado total (en minutos).

Responde SOLO en formato Markdown, por ejemplo:

Objetivo: ...
Tiempo estimado: 45 minutos
Actividades:
- ...
- ...
- ...
"""
            respuesta = self.llm.invoke(prompt)
            descripcion = respuesta.content if hasattr(respuesta, "content") else str(respuesta)

            sesiones.append(
                {
                    "tipo": tipo,
                    "fecha": fecha.isoformat(),
                    "descripcion": descripcion,
                }
            )

        return {
            "tema": tema,
            "fecha_inicio": fecha_inicio.isoformat(),
            "sesiones": sesiones,
        }
