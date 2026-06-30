import customtkinter as ctk
import threading
import requests
import webbrowser
import os

from tkinter import filedialog, messagebox
from core.installer import Installer


APP_VERSION = "1.0.0"


class LauncherUI:

    def __init__(self):

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.app = ctk.CTk()
        self.app.title("Minecraft Mod Installer")
        self.app.geometry("1000x600")
        self.app.resizable(False, False)

        self.minecraft_path = None
        self.installer = Installer()

        self.crear_interfaz()

    # =========================
    # UI
    # =========================
    def crear_interfaz(self):

        self.left = ctk.CTkFrame(self.app, width=220, corner_radius=0)
        self.left.pack(side="left", fill="y")

        ctk.CTkLabel(
            self.left,
            text="MINECRAFT\nINSTALLER",
            font=("Segoe UI", 24, "bold")
        ).pack(pady=40)

        self.right = ctk.CTkFrame(self.app)
        self.right.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        self.estado = ctk.CTkLabel(self.right, text="🟢 Esperando", font=("Segoe UI", 18))
        self.estado.pack(anchor="w", pady=(20, 10))

        self.progress = ctk.CTkProgressBar(self.right, width=650)
        self.progress.pack(pady=10)
        self.progress.set(0)

        self.log = ctk.CTkTextbox(self.right, width=700, height=320)
        self.log.pack(pady=20)
        self.log.insert("end", "Bienvenido\n")

        botones = ctk.CTkFrame(self.right, fg_color="transparent")
        botones.pack(pady=10)

        self.install_btn = ctk.CTkButton(
            botones,
            text="Instalar Mods",
            width=220,
            command=self.iniciar_instalacion
        )
        self.install_btn.grid(row=0, column=0, padx=10)

        self.select_btn = ctk.CTkButton(
            botones,
            text="Seleccionar .minecraft",
            width=220,
            command=self.seleccionar_carpeta
        )
        self.select_btn.grid(row=0, column=1, padx=10)

        self.update_btn = ctk.CTkButton(
            botones,
            text="Buscar actualización",
            width=220,
            command=self.check_update
        )
        self.update_btn.grid(row=0, column=2, padx=10)

    # =========================
    # SELECCION CARPETA
    # =========================
    def seleccionar_carpeta(self):

        messagebox.showinfo(
            "IMPORTANTE",
            "Selecciona la carpeta .minecraft (NO la carpeta mods)"
        )

        folder = filedialog.askdirectory(title="Selecciona tu carpeta .minecraft")

        if not folder:
            return

        mods_path = os.path.join(folder, "mods")

        if not os.path.exists(mods_path):
            messagebox.showwarning(
                "Carpeta incorrecta",
                "No parece ser .minecraft (falta carpeta mods)"
            )
            return

        self.minecraft_path = folder
        self.installer.set_custom_minecraft(folder)

        self.estado.configure(text="🟡 Ruta personalizada")
        self.log.insert("end", f"\n📁 .minecraft seleccionado:\n{folder}\n")

    # =========================
    # UPDATE SYSTEM
    # =========================
    def check_update(self):

        def _check():

            try:
                url = "https://raw.githubusercontent.com/JordiMarrufo/Launcher-minecraft-mod/main/version.json"
                r = requests.get(url, timeout=10)
                data = r.json()

                latest = data["version"]

                if latest != APP_VERSION:

                    self.log.insert("end", f"\n🟡 Nueva versión: {latest}\n")

                    messagebox.showinfo(
                        "Actualización disponible",
                        f"Versión nueva: {latest}\nTu versión: {APP_VERSION}"
                    )

                    webbrowser.open(data["url"])

                else:
                    messagebox.showinfo(
                        "Actualización",
                        "Ya tienes la última versión"
                    )

            except Exception as e:
                messagebox.showerror("Error update", str(e))

        threading.Thread(target=_check).start()

    # =========================
    # THREAD FIX
    # =========================
    def iniciar_instalacion(self):
        threading.Thread(target=self.instalar).start()

    # =========================
    # INSTALAR MODS
    # =========================
    def instalar(self):

        self.log.delete("1.0", "end")
        self.progress.set(0)

        self.log.insert("end", "🔍 Buscando Minecraft...\n")

        carpeta = self.installer.buscar_minecraft()

        if not carpeta:
            self.log.insert("end", "❌ Minecraft no encontrado\n")
            return

        self.log.insert("end", f"📂 {carpeta}\n\n")

        self.log.insert("end", "📡 Descargando modpack...\n")

        url_json = "https://raw.githubusercontent.com/JordiMarrufo/Mods-1.20.1/main/modpack.json"
        data = self.installer.descargar_modpack(url_json)

        if not data:
            self.log.insert("end", "❌ Error cargando modpack.json\n")
            return

        mods = data["mods"]
        total = len(mods)

        self.log.insert("end", f"📦 Instalando {total} mods...\n\n")

        ok, result = self.installer.instalar_mods(data)

        if not ok:
            self.log.insert("end", f"❌ {result}\n")
            return

        # progreso visual seguro
        for i in range(total):

            self.log.insert("end", f"✔ {i+1}/{total} instalado\n")
            self.progress.set((i + 1) / total)
            self.app.update()

        self.estado.configure(text="🟢 Instalado")
        self.log.insert("end", "\n🎉 Instalación completada\n")

    # =========================
    # START
    # =========================
    def iniciar(self):
        self.app.mainloop()