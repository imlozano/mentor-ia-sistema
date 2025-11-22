# tests/test_vision_local.py

from pathlib import Path

from src.ocr_vision import crear_cliente_vision, extraer_texto_imagen_vision


def main():
    # Ruta a tu imagen de prueba
    ruta_imagen = Path("data/imagenes/historia-c-c++.png")

    if not ruta_imagen.exists():
        print(f"[ERROR] No existe la imagen: {ruta_imagen}")
        return

    client = crear_cliente_vision()
    texto = extraer_texto_imagen_vision(client, ruta_imagen)

    print("=== TEXTO EXTRAÍDO ===")
    print(texto)


if __name__ == "__main__":
    main()
