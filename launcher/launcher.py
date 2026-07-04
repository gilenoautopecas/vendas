"""
GSales Launcher
Sobe o servidor Django, abre o navegador e exibe ícone na bandeja do sistema.
Empacote com build.bat no Windows para gerar GSales.exe.
"""

import subprocess
import sys
import time
import webbrowser
import socket
import threading
from pathlib import Path
from tkinter import messagebox
import tkinter as tk

import pystray
from PIL import Image, ImageDraw


def mostrar_erro(mensagem):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("GSales — Erro", mensagem)
    root.destroy()


def pasta_projeto():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def porta_livre(host="127.0.0.1", porta=8000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, porta)) != 0


def aguardar_servidor(host="127.0.0.1", porta=8000, timeout=60):
    inicio = time.time()
    while time.time() - inicio < timeout:
        if not porta_livre(host, porta):
            return True
        time.sleep(0.4)
    return False


def recursos_dir():
    """Pasta onde estão os arquivos embutidos pelo PyInstaller."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def criar_icone():
    """Carrega o ícone do sistema, ou gera um fallback se não encontrar."""
    base = recursos_dir()
    for nome in ("gsales.png", "gsales.ico"):
        caminho = base / nome
        if caminho.exists():
            return Image.open(caminho).convert("RGBA")

    # Fallback: gera ícone simples em memória
    img = Image.new("RGBA", (64, 64), color="#4f46e5")
    draw = ImageDraw.Draw(img)
    draw.text((18, 14), "G", fill="white")
    return img


def main():
    projeto = pasta_projeto()
    python  = projeto / "venv" / "Scripts" / "python.exe"
    manage  = projeto / "manage.py"

    if not python.exists():
        mostrar_erro(f"Python do venv não encontrado em:\n{python}")
        return

    if not manage.exists():
        mostrar_erro(f"manage.py não encontrado em:\n{manage}")
        return

    # Servidor já rodando — só abre navegador
    if not porta_livre():
        webbrowser.open("http://127.0.0.1:8000")
        return

    log_path = projeto / "gsales.log"
    log = open(log_path, "w", encoding="utf-8")

    processo = subprocess.Popen(
        [str(python), str(manage), "runserver", "--noreload"],
        cwd=str(projeto),
        creationflags=subprocess.CREATE_NO_WINDOW,
        stdout=log,
        stderr=log,
    )

    if not aguardar_servidor():
        mostrar_erro(
            f"O servidor não respondeu em 60 segundos.\n"
            f"Verifique: {log_path}\n\n"
            f"Ou acesse manualmente: http://127.0.0.1:8000"
        )
        processo.terminate()
        return

    webbrowser.open("http://127.0.0.1:8000")

    # ── Bandeja do sistema ──────────────────────────────────────
    def abrir(icon, item):
        webbrowser.open("http://127.0.0.1:8000")

    def fechar(icon, item):
        icon.stop()
        processo.terminate()

    menu = pystray.Menu(
        pystray.MenuItem("Abrir GSales", abrir, default=True),
        pystray.MenuItem("Fechar", fechar),
    )

    icon = pystray.Icon("GSales", criar_icone(), "GSales", menu)
    icon.run()


if __name__ == "__main__":
    main()
