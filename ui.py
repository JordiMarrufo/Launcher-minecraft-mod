import customtkinter as ctk
import threading
import requests
import webbrowser
import os
import sys
import tkinter.font as tkfont
from core.updater import Updater
from tkinter import filedialog, messagebox
from core.installer import Installer


APP_VERSION = "1.0.5"  # Actualiza esta versión según corresponda


# =====================================================
# PALETA DE COLORES ESTILO MINECRAFT
# =====================================================
class MCColors:
    BG_STONE      = "#262626"   # fondo general (piedra oscura)
    PANEL_DIRT    = "#3A2E22"   # panel lateral (tierra)
    PANEL_STONE   = "#2F2F2F"   # panel derecho (piedra)
    GRASS_TOP     = "#5D8A3A"   # franja superior tipo bloque de pasto
    GRASS_DARK    = "#3F5F28"
    WOOD          = "#7A5230"   # marcos tipo madera
    WOOD_DARK     = "#4F341C"

    BUTTON_FACE   = "#8B8B8B"   # gris botón clásico de Minecraft GUI
    BUTTON_HOVER  = "#A6A6A6"
    BUTTON_PRESS  = "#6E6E6E"
    BUTTON_BORDER = "#1E1E1E"

    TEXT_WHITE    = "#FFFFFF"
    TEXT_GRAY     = "#C6C6C6"
    TEXT_YELLOW   = "#FFFF55"   # texto "encantado" / títulos
    TEXT_GREEN    = "#55FF55"
    TEXT_RED      = "#FF5555"

    LOG_BG        = "#0A0A0A"
    PROGRESS_BG   = "#1A1A1A"
    PROGRESS_FILL = "#55AA00"   # verde barra de experiencia
    PROGRESS_BORDER = "#000000"


def pixel_font(size=14, bold=True):
    """Intenta usar una fuente tipo pixel-art si está instalada,
    si no, recurre a una monoespaciada en negrita que da un aire
    'bloque' similar al de Minecraft."""
    preferred = ["Minecraftia", "Press Start 2P", "04b03", "Pixel Emulator"]
    installed = set(tkfont.families())
    for name in preferred:
        if name in installed:
            return (name, size)
    return ("Consolas", size, "bold" if bold else "normal")


class LauncherUI:

    def __init__(self):

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.app = ctk.CTk()
        self.app.title("Last Hope - Launcher - Mods")
        self.app.geometry("1000x600")
        self.app.resizable(False, False)
        self.app.configure(fg_color=MCColors.BG_STONE)

        self.updater = Updater()
        self.minecraft_path = None
        self.installer = Installer()

        self.crear_interfaz()

    # =========================
    # UI
    # =========================
    def crear_interfaz(self):

        # ---------- SIDEBAR (estilo "tierra" con franja de "pasto") ----------
        self.left = ctk.CTkFrame(
            self.app, width=220, corner_radius=0,
            fg_color=MCColors.PANEL_DIRT,
            border_width=4, border_color=MCColors.WOOD_DARK
        )
        self.left.pack(side="left", fill="y")
        self.left.pack_propagate(False)

        # franja superior tipo "bloque de pasto"
        grass_strip = ctk.CTkFrame(
            self.left, height=14, corner_radius=0,
            fg_color=MCColors.GRASS_TOP
        )
        grass_strip.pack(fill="x", side="top")

        # Título con efecto de "sombra" tipo letras de Minecraft
        title_container = ctk.CTkFrame(self.left, fg_color="transparent")
        title_container.pack(pady=(40, 10), padx=10)

        shadow = ctk.CTkLabel(
            title_container,
            text="MODS\nINSTALLER\nLAST HOPE",
            font=pixel_font(20, True),
            text_color=MCColors.WOOD_DARK,
            justify="center"
        )
        shadow.place(x=3, y=3)

        ctk.CTkLabel(
            title_container,
            text="MODS\nINSTALLER\nLAST HOPE",
            font=pixel_font(20, True),
            text_color=MCColors.TEXT_YELLOW,
            justify="center"
        ).pack()

        ctk.CTkLabel(
            self.left,
            text=f"v{APP_VERSION}",
            font=pixel_font(12, False),
            text_color=MCColors.TEXT_GRAY
        ).pack(pady=(0, 30))

        # bloque decorativo inferior (simula textura de tierra apilada)
        deco = ctk.CTkFrame(self.left, fg_color=MCColors.WOOD, height=8, corner_radius=0)
        deco.pack(side="bottom", fill="x")

        # ---------- PANEL DERECHO (estilo "piedra") ----------
        self.right = ctk.CTkFrame(
            self.app, fg_color=MCColors.PANEL_STONE, corner_radius=0,
            border_width=4, border_color=MCColors.BUTTON_BORDER
        )
        self.right.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        self.estado = ctk.CTkLabel(
            self.right, text="🟢 Esperando",
            font=pixel_font(16, True),
            text_color=MCColors.TEXT_GREEN
        )
        self.estado.pack(anchor="w", padx=20, pady=(20, 10))

        # ---------- BARRA DE PROGRESO (estilo barra de experiencia) ----------
        progress_frame = ctk.CTkFrame(
            self.right, fg_color=MCColors.PROGRESS_BORDER,
            corner_radius=0, border_width=2, border_color=MCColors.BUTTON_BORDER
        )
        progress_frame.pack(padx=20, pady=10, fill="x")

        self.progress = ctk.CTkProgressBar(
            progress_frame, width=650, height=18,
            corner_radius=0,
            fg_color=MCColors.PROGRESS_BG,
            progress_color=MCColors.PROGRESS_FILL
        )
        self.progress.pack(padx=4, pady=4, fill="x")
        self.progress.set(0)

        # ---------- CONSOLA / LOG (estilo chat de Minecraft) ----------
        self.log = ctk.CTkTextbox(
            self.right, width=700, height=320,
            corner_radius=0,
            fg_color=MCColors.LOG_BG,
            text_color=MCColors.TEXT_WHITE,
            font=("Consolas", 13),
            border_width=2, border_color=MCColors.BUTTON_BORDER
        )
        self.log.pack(padx=20, pady=20, fill="both", expand=True)
        self.log.insert("end", "§a[Sistema]§r Bienvenido a Last Hope Mods Installer\n")

        # ---------- BOTONES (estilo botón clásico de menú de Minecraft) ----------
        botones = ctk.CTkFrame(self.right, fg_color="transparent")
        botones.pack(pady=(0, 20))

        btn_kwargs = dict(
            corner_radius=0,
            fg_color=MCColors.BUTTON_FACE,
            hover_color=MCColors.BUTTON_HOVER,
            text_color=MCColors.TEXT_WHITE,
            font=pixel_font(13, True),
            border_width=3,
            border_color=MCColors.BUTTON_BORDER,
            width=170,
            height=40
        )

        self.install_btn = ctk.CTkButton(
            botones, text="⛏ Instalar Mods",
            command=self.iniciar_instalacion, **btn_kwargs
        )
        self.install_btn.grid(row=0, column=0, padx=6, pady=8)

        self.select_btn = ctk.CTkButton(
            botones, text="📁 Seleccionar .minecraft",
            command=self.seleccionar_carpeta, **btn_kwargs
        )
        self.select_btn.grid(row=0, column=1, padx=6, pady=8)

        self.check_update_btn = ctk.CTkButton(
            botones, text="🔍 Buscar actualización",
            command=self.check_update, **btn_kwargs
        )
        self.check_update_btn.grid(row=0, column=2, padx=6, pady=8)

        update_btn_kwargs = dict(btn_kwargs)
        update_btn_kwargs["fg_color"] = MCColors.GRASS_TOP
        update_btn_kwargs["hover_color"] = MCColors.GRASS_DARK

        self.update_btn = ctk.CTkButton(
            botones, text="⬆ Actualizar",
            command=self.actualizar_app,
            state="disabled",
            **update_btn_kwargs
        )
        self.update_btn.grid(row=0, column=3, padx=6, pady=8)

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

        self.estado.configure(text="🟡 Ruta personalizada", text_color=MCColors.TEXT_YELLOW)
        self.log.insert("end", f"\n📁 .minecraft seleccionado:\n{folder}\n")

    # =========================
    # UPDATE SYSTEM
    # =========================
    def check_update(self):

        def _check():
            try:
                url = "https://raw.githubusercontent.com/JordiMarrufo/Launcher-minecraft-mod/main/version.json"
                r = requests.get(url, timeout=10)
                r.raise_for_status()

                data = r.json()

                latest = str(data.get("version", "")).strip()
                app_version = str(APP_VERSION).strip()

                print("APP VERSION:", app_version)
                print("LATEST:", latest)
                print("RAW JSON:", data)

                if not latest:
                    messagebox.showerror("Error", "No se encontró la versión en GitHub")
                    return

                if latest != app_version:
                    self.update_btn.configure(state="normal")
                    self.log.insert("end", f"\n🟡 Nueva versión: {latest}\n")
                    self.estado.configure(text="🟡 Update disponible", text_color=MCColors.TEXT_YELLOW)

                    messagebox.showinfo(
                        "Actualización disponible",
                        f"Nueva versión: {latest}\nTu versión: {app_version}"
                    )

                    webbrowser.open(
                        data.get("url", "https://github.com/JordiMarrufo/Launcher-minecraft-mod/releases/latest")
                    )

                else:
                    messagebox.showinfo(
                        "Actualización",
                        f"Ya tienes la última versión ({app_version})"
                    )

                    self.update_btn.configure(state="disabled")
                    self.estado.configure(text="🟢 Actualizado", text_color=MCColors.TEXT_GREEN)

            except requests.exceptions.RequestException as e:
                messagebox.showerror("Error de red", str(e))

            except ValueError:
                messagebox.showerror("Error", "JSON inválido en version.json")

            except Exception as e:
                messagebox.showerror("Error inesperado", str(e))

        threading.Thread(target=_check, daemon=True).start()

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
            self.estado.configure(text="🔴 Error", text_color=MCColors.TEXT_RED)
            return

        self.log.insert("end", f"📂 {carpeta}\n\n")

        self.log.insert("end", "📡 Descargando modpack...\n")

        url_json = "https://raw.githubusercontent.com/JordiMarrufo/Mods-1.20.1/main/modpack.json"
        data = self.installer.descargar_modpack(url_json)

        if not data:
            self.log.insert("end", "❌ Error cargando modpack.json\n")
            self.estado.configure(text="🔴 Error", text_color=MCColors.TEXT_RED)
            return

        mods = data["mods"]
        total = len(mods)

        self.log.insert("end", f"📦 Instalando {total} mods...\n\n")

        ok, result = self.installer.instalar_mods(data)

        if not ok:
            self.log.insert("end", f"❌ {result}\n")
            self.estado.configure(text="🔴 Error", text_color=MCColors.TEXT_RED)
            return

        # progreso visual seguro
        for i in range(total):

            self.log.insert("end", f"✔ {i+1}/{total} instalado\n")
            self.progress.set((i + 1) / total)
            self.app.update()

        self.estado.configure(text="🟢 Instalado", text_color=MCColors.TEXT_GREEN)
        self.log.insert("end", "\n🎉 Instalación completada\n")

    # =========================
    # START
    # =========================
    def iniciar(self):
        self.app.mainloop()

    # =========================
    # ACTUALIZAR APP
    # =========================
    def actualizar_app(self):
        try:
            self.log.insert("end", "\n⬇ Descargando actualización...\n")

            url = "https://github.com/JordiMarrufo/Launcher-minecraft-mod/releases/latest/download/LastHopeLauncher.exe"

            r = requests.get(url, stream=True)
            r.raise_for_status()

            # Ruta real del .exe que se está ejecutando ahora mismo.
            # Cuando la app está compilada con PyInstaller, sys.executable
            # apunta exactamente a "LastHopeLauncher.exe" (con su nombre real),
            # así que NO hay que inventar nombres como "app.exe".
            if getattr(sys, "frozen", False):
                current_exe = sys.executable
            else:
                # Si se ejecuta como script .py (modo desarrollo), simulamos
                # la ruta que tendría el exe final para poder probar el flujo.
                current_exe = os.path.abspath("LastHopeLauncher.exe")

            exe_dir = os.path.dirname(current_exe)
            exe_name = os.path.basename(current_exe)

            # Archivo temporal de descarga, en la MISMA carpeta que el exe real.
            new_exe = os.path.join(exe_dir, f"{exe_name}.update")

            # guardar el nuevo exe descargado
            with open(new_exe, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

            self.log.insert("end", "✔ Descarga completada\n")

            # Script .bat que:
            # 1. Espera a que la app actual se cierre por completo (libera el .exe)
            # 2. Borra el exe viejo
            # 3. Renombra el nuevo archivo descargado con el MISMO nombre original
            # 4. Vuelve a abrir la app ya actualizada
            # 5. Se autoelimina
            bat_path = os.path.join(exe_dir, "update.bat")

            with open(bat_path, "w") as f:
                f.write(f"""@echo off
:wait_close
tasklist /fi "imagename eq {exe_name}" | find /i "{exe_name}" >nul
if not errorlevel 1 (
    timeout /t 1 >nul
    goto wait_close
)
del /f /q "{current_exe}"
move /y "{new_exe}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
""")

            messagebox.showinfo(
                "Update listo",
                "Se cerrará la app para actualizar."
            )

            # cerrar app (libera el archivo .exe para que el .bat pueda reemplazarlo)
            self.app.destroy()

            # ejecutar updater
            os.startfile(bat_path)

        except Exception as e:
            messagebox.showerror("Error update", str(e))