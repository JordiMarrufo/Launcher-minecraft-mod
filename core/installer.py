import os
import requests
from core.minecraft import obtener_carpeta_minecraft


class Installer:

    def __init__(self):
        self.custom_path = None

    def set_custom_minecraft(self, path):
        self.custom_path = path

    def buscar_minecraft(self):
        # si el usuario eligió ruta manual, la usa primero
        if self.custom_path and os.path.exists(self.custom_path):
            return self.custom_path

        return obtener_carpeta_minecraft()

    def descargar_modpack(self, url_json):

        try:
            r = requests.get(url_json, timeout=10)
            r.raise_for_status()
            return r.json()

        except Exception as e:
            print("Error descargando modpack:", e)
            return None

    def instalar_mods(self, data):

        minecraft = self.buscar_minecraft()

        if not minecraft:
            return False, "Minecraft no encontrado"

        mods_folder = os.path.join(minecraft, "mods")
        os.makedirs(mods_folder, exist_ok=True)

        mods = data["mods"]
        instalados = []

        base_url = "https://raw.githubusercontent.com/JordiMarrufo/Mods-1.20.1/main/mods/"

        for mod in mods:

            url = base_url + mod
            destino = os.path.join(mods_folder, mod)

            if os.path.exists(destino):
                instalados.append(mod)
                continue

            try:
                r = requests.get(url, stream=True, timeout=20)
                r.raise_for_status()

                with open(destino, "wb") as f:
                    for chunk in r.iter_content(1024):
                        if chunk:
                            f.write(chunk)

                instalados.append(mod)

            except Exception as e:
                print(f"Error instalando {mod}: {e}")

        return True, instalados