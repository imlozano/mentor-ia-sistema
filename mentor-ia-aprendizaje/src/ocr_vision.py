# # src/ocr_vision.py

# from typing import Optional

# from google.cloud import vision


# def crear_cliente_vision() -> vision.ImageAnnotatorClient:
#     """
#     Crea un cliente de Google Cloud Vision.

#     Requiere que la variable de entorno GOOGLE_APPLICATION_CREDENTIALS
#     apunte al JSON de credenciales de la cuenta de servicio.
#     """
#     return vision.ImageAnnotatorClient()


# def extraer_texto_imagen_vision(
#     ruta_imagen: str,
#     client: Optional[vision.ImageAnnotatorClient] = None,
# ) -> str:
#     """
#     Usa Google Cloud Vision para extraer texto de una imagen (PNG/JPG).

#     Devuelve todo el texto detectado como un string.
#     """
#     if client is None:
#         client = crear_cliente_vision()

#     with open(ruta_imagen, "rb") as f:
#         content = f.read()

#     image = vision.Image(content=content)

#     # DOCUMENT_TEXT_DETECTION suele dar mejor resultado que text_detection
#     response = client.document_text_detection(image=image)

#     if response.error.message:
#         # En un proyecto real, mejor loguear y devolver "" en vez de romper.
#         raise RuntimeError(f"Error en Vision OCR: {response.error.message}")

#     # full_text_annotation.text trae TODO el texto del documento
#     if response.full_text_annotation and response.full_text_annotation.text:
#         return response.full_text_annotation.text

#     # fallback por si no viene full_text_annotation
#     if response.text_annotations:
#         return response.text_annotations[0].description

#     return ""

# """
# ocr_vision.py

# Helper para crear el cliente de Google Cloud Vision
# usando el archivo de credenciales que apunta
# GOOGLE_APPLICATION_CREDENTIALS.
# """

# import os
# from pathlib import Path

# from google.cloud import vision_v1 as vision
# from google.oauth2 import service_account


# def crear_cliente_vision() -> vision.ImageAnnotatorClient:
#     """
#     Crea y devuelve un cliente de Google Cloud Vision.

#     - Usa la variable de entorno GOOGLE_APPLICATION_CREDENTIALS.
#     - Valida que el archivo exista.
#     - Carga las credenciales explícitamente (sin depender de google.auth.default()).
#     """
#     cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

#     if not cred_path:
#         raise RuntimeError(
#             "GOOGLE_APPLICATION_CREDENTIALS no está definida. "
#             "Configúrala en tu shell apuntando al archivo JSON del service account."
#         )

#     ruta = Path(cred_path)
#     if not ruta.exists():
#         raise RuntimeError(
#             f"El archivo de credenciales no existe en: {ruta}. "
#             "Revisa la ruta en tu variable GOOGLE_APPLICATION_CREDENTIALS."
#         )

#     # Cargar credenciales explícitamente desde el JSON
#     credentials = service_account.Credentials.from_service_account_file(str(ruta))

#     # Crear el cliente de Vision usando esas credenciales
#     return vision.ImageAnnotatorClient(credentials=credentials)

"""
ocr_vision.py

Helpers para trabajar con Google Cloud Vision:

- crear_cliente_vision(): crea el cliente usando el JSON de credenciales
  apuntado por GOOGLE_APPLICATION_CREDENTIALS.
- extraer_texto_imagen_vision(): dado un path de imagen, devuelve el texto
  detectado usando Vision (document_text_detection).
"""

import os
from pathlib import Path

from dotenv import load_dotenv          # <- NUEVO
from google.cloud import vision_v1 as vision
from google.oauth2 import service_account

# Cargar variables desde .env
load_dotenv()                           # <- NUEVO


def crear_cliente_vision() -> vision.ImageAnnotatorClient:
    """
    Crea y devuelve un cliente de Google Cloud Vision.

    Usa explícitamente el archivo JSON indicado en la variable
    de entorno GOOGLE_APPLICATION_CREDENTIALS.
    """
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not cred_path:
        raise RuntimeError(
            "GOOGLE_APPLICATION_CREDENTIALS no está definida. "
            "Configúrala en tu shell apuntando al archivo JSON del service account."
        )

    ruta = Path(cred_path)
    if not ruta.exists():
        raise RuntimeError(
            f"El archivo de credenciales no existe en: {ruta}. "
            "Revisa la ruta en tu variable GOOGLE_APPLICATION_CREDENTIALS."
        )

    # Cargar credenciales explícitamente desde el JSON
    credentials = service_account.Credentials.from_service_account_file(str(ruta))

    # Crear el cliente de Vision usando esas credenciales
    return vision.ImageAnnotatorClient(credentials=credentials)


# def extraer_texto_imagen_vision(
#     client: vision.ImageAnnotatorClient,
#     image_path: str,
# ) -> str:
#     """
#     Extrae texto de una imagen usando Google Cloud Vision.

#     - client: instancia creada con crear_cliente_vision()
#     - image_path: ruta local a la imagen (PNG, JPG, etc.)

#     Devuelve:
#         El texto completo detectado (string). Si no hay texto, devuelve "".
#     """
#     from google.api_core.exceptions import GoogleAPIError

#     ruta = Path(image_path)
#     if not ruta.exists():
#         raise FileNotFoundError(f"La imagen no existe: {ruta}")

#     try:
#         with ruta.open("rb") as f:
#             content = f.read()

#         image = vision.Image(content=content)

#         # document_text_detection suele ir mejor para texto denso (apuntes, PDFs convertidos a imagen, etc.)
#         response = client.document_text_detection(image=image)

#         if response.error.message:
#             # No hacemos raise para no tumbar todo el servidor, solo avisamos.
#             print(f"[VISION][ERROR] {response.error.message}")
#             return ""

#         if response.full_text_annotation and response.full_text_annotation.text:
#             return response.full_text_annotation.text.strip()

#         # Fallback: intentar con text_annotations
#         if response.text_annotations:
#             return response.text_annotations[0].description.strip()

#         return ""

#     except GoogleAPIError as e:
#         print(f"[VISION][EXCEPTION] Error llamando a Vision API: {e}")
#         return ""
#     except Exception as e:
#         print(f"[VISION][EXCEPTION] Error inesperado procesando la imagen: {e}")
#         return ""

def extraer_texto_imagen_vision(
    ruta_imagen: str,
    client: vision.ImageAnnotatorClient | None = None,
) -> str:
    """
    Extrae texto usando Google Vision (document_text_detection)
    a partir de una ruta local de imagen.
    """
    from google.api_core.exceptions import GoogleAPIError

    if client is None:
        client = crear_cliente_vision()

    ruta = Path(ruta_imagen)
    if not ruta.exists():
        raise FileNotFoundError(f"La imagen no existe: {ruta}")

    try:
        with ruta.open("rb") as f:
            content = f.read()

        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)

        if response.error.message:
            print(f"[VISION][ERROR] {response.error.message}")
            return ""

        if response.full_text_annotation and response.full_text_annotation.text:
            return response.full_text_annotation.text.strip()

        if response.text_annotations:
            return response.text_annotations[0].description.strip()

        return ""

    except GoogleAPIError as e:
        print(f"[VISION][EXCEPTION] Error llamando a Vision API: {e}")
        return ""

    except Exception as e:
        print(f"[VISION][EXCEPTION] Error inesperado: {e}")
        return ""
