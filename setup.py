import sys
import os
from cx_Freeze import setup, Executable

# Caminho absoluto da pasta do projeto
base_dir = os.path.dirname(os.path.abspath(__file__))

# Caminho absoluto da pasta 'assets' e do arquivo .env
assets_dir = os.path.join(base_dir, "assets")
env_file = os.path.join(base_dir, ".env")

build_exe_options = {
    "packages": ["os", "tkinter", "dotenv"],
    "include_files": [
        (assets_dir, "assets"),  # copia toda a pasta assets para o build
        (env_file, ".env"),       # copia o arquivo .env
    ],
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"  # evita console junto do Tkinter

setup(
    name="emby-karaoke",
    version="0.1",
    description="Emby Karaoke",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)],
)
