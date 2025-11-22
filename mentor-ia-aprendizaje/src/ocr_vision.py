# """
# ocr_vision.py

# Helpers para trabajar con Google Cloud Vision:

# - crear_cliente_vision(): crea el cliente usando el JSON de credenciales
#   apuntado por GOOGLE_APPLICATION_CREDENTIALS.
# - extraer_texto_imagen_vision(): dado un path de imagen, devuelve el texto
#   detectado usando Vision (document_text_detection).
# """

# import os
# from pathlib import Path

# from dotenv import load_dotenv          # <- NUEVO
# from google.cloud import vision_v1 as vision
# from google.oauth2 import service_account

# import tempfile #NUEVO

# # Cargar variables desde .env
# load_dotenv()                           # <- NUEVO


# def crear_cliente_vision() -> vision.ImageAnnotatorClient:
#     """
#     Crea y devuelve un cliente de Google Cloud Vision.

#     Usa explícitamente el archivo JSON indicado en la variable
#     de entorno GOOGLE_APPLICATION_CREDENTIALS.
#     """
#     cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

#     if not cred_path:
#         raise RuntimeError(
#             "GOOGLE_APPLICATION_CREDENTIALS no está definida. "
#             "Configúrala en tu shell apuntando al archivo JSON del service account."
#         )
#         # 1) Si existe GOOGLE_VISION_KEY (Railway), crear credenciales desde JSON en string
#         # json_key_raw = os.getenv("GOOGLE_VISION_KEY")
#         # if json_key_raw:
#         #     try:
#         #         from google.oauth2.service_account import Credentials
#         #         import json

#         #         json_dict = json.loads(json_key_raw)
#         #         credentials = Credentials.from_service_account_info(json_dict)
#         #         return vision.ImageAnnotatorClient(credentials=credentials)
#         #     except Exception as e:
#         #         raise RuntimeError(f"Error creando credenciales desde GOOGLE_VISION_KEY: {e}")

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


# def extraer_texto_imagen_vision(
#     ruta_imagen: str,
#     client: vision.ImageAnnotatorClient | None = None,
# ) -> str:
#     """
#     Extrae texto usando Google Vision (document_text_detection)
#     a partir de una ruta local de imagen.
#     """
#     from google.api_core.exceptions import GoogleAPIError

#     if client is None:
#         client = crear_cliente_vision()

#     ruta = Path(ruta_imagen)
#     if not ruta.exists():
#         raise FileNotFoundError(f"La imagen no existe: {ruta}")

#     try:
#         with ruta.open("rb") as f:
#             content = f.read()

#         image = vision.Image(content=content)
#         response = client.document_text_detection(image=image)

#         if response.error.message:
#             print(f"[VISION][ERROR] {response.error.message}")
#             return ""

#         if response.full_text_annotation and response.full_text_annotation.text:
#             return response.full_text_annotation.text.strip()

#         if response.text_annotations:
#             return response.text_annotations[0].description.strip()

#         return ""

#     except GoogleAPIError as e:
#         print(f"[VISION][EXCEPTION] Error llamando a Vision API: {e}")
#         return ""

#     except Exception as e:
#         print(f"[VISION][EXCEPTION] Error inesperado: {e}")
#         return ""


"""
ocr_vision.py

Helpers para trabajar con Google Cloud Vision:

- crear_cliente_vision(): crea el cliente usando las credenciales
  de Google Cloud Vision (desde archivo local o desde variable de entorno).
- extraer_texto_imagen_vision(): dado un path de imagen, devuelve el texto
  detectado usando Vision (document_text_detection).
"""

import os
import json
from pathlib import Path

from dotenv import load_dotenv
# from google.cloud import vision_v1 as vision <- NO FUNCIONA EN RAILWAY
from google.cloud import vision #NUEVO
from google.oauth2 import service_account

# Cargar variables desde .env (solo tiene efecto en local)
load_dotenv()


def crear_cliente_vision() -> vision.ImageAnnotatorClient:
    """
    Crea y devuelve un cliente de Google Cloud Vision.

    Prioridad:
    1) Si existe GOOGLE_VISION_KEY (JSON en string, ideal para Railway), 
       crea credenciales desde ahí.
    2) Si no existe, usa GOOGLE_APPLICATION_CREDENTIALS apuntando a un
       archivo .json local (modo desarrollo).
    """

    # 1) Modo Railway / producción: JSON completo en una variable de entorno
    json_key_raw = os.getenv("GOOGLE_VISION_KEY")
    if json_key_raw:
        try:
            json_dict = json.loads(json_key_raw)
            credentials = service_account.Credentials.from_service_account_info(json_dict)
            return vision.ImageAnnotatorClient(credentials=credentials)
        except Exception as e:
            raise RuntimeError(f"Error creando credenciales desde GOOGLE_VISION_KEY: {e}")

    # 2) Modo local: ruta a archivo .json
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        raise RuntimeError(
            "No se encontró ninguna credencial de Vision.\n"
            "- Define GOOGLE_VISION_KEY (con el JSON completo) para producción, o\n"
            "- Define GOOGLE_APPLICATION_CREDENTIALS apuntando al archivo .json en local."
        )

    ruta = Path(cred_path)
    if not ruta.exists():
        raise RuntimeError(
            f"El archivo de credenciales no existe en: {ruta}. "
            "Revisa la ruta en tu variable GOOGLE_APPLICATION_CREDENTIALS."
        )

    # Cargar credenciales explícitamente desde el JSON local
    credentials = service_account.Credentials.from_service_account_file(str(ruta))

    # Crear el cliente de Vision usando esas credenciales
    return vision.ImageAnnotatorClient(credentials=credentials)


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
