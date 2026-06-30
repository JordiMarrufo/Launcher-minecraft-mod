import os

def obtener_carpeta_minecraft():
    ruta = os.path.join(
        os.getenv("APPDATA"),
        ".minecraft"
    )

    if os.path.exists(ruta):
        return ruta

    return None