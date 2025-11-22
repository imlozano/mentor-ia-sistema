"""
extraccion.py

Funciones para cargar documentos desde el sistema de archivos
(PDF, TXT, etc.) y devolver su texto.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader


@dataclass
class DocumentoFuente:
    path: Path
    tipo: str = "pdf"  # "pdf", "txt", etc.


def listar_documentos_ejemplo(base_dir: str = "data/ejemplos") -> List[DocumentoFuente]:
    """
    Lista los documentos disponibles en data/ejemplos.

    Más adelante podrás filtrar por curso, tema, etc.
    """
    base = Path(base_dir)
    documentos: List[DocumentoFuente] = []

    for ruta in base.glob("**/*"):
        if ruta.is_file():
            sufijo = ruta.suffix.lower()
            if sufijo in {".pdf", ".txt"}:
                documentos.append(
                    DocumentoFuente(path=ruta, tipo=sufijo.lstrip("."))
                )

    return documentos


def extraer_texto_documento(doc: DocumentoFuente) -> str:
    """
    Extrae el texto de un documento según su tipo.
    """
    if doc.tipo == "pdf":
        loader = PyPDFLoader(str(doc.path))
        pages = loader.load()
        # Unimos todas las páginas en un solo texto
        full_text = "\n".join(page.page_content for page in pages)
        return full_text

    if doc.tipo == "txt":
        return doc.path.read_text(encoding="utf-8")

    # Si es otro tipo, de momento no lo soportamos
    raise ValueError(f"Tipo de documento no soportado: {doc.tipo}")
