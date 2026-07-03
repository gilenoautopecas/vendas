"""
GSales Launcher
Sobe o servidor Django e abre o navegador automaticamente.
Empacote com build.bat no Windows para gerar GSales.exe.
"""

import subprocess
import sys
import time
import webbrowser
import socket
from pathlib import Path
from tkinter import messagebox
import tkinter as tk


def mostrar_erro(mensagem):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("GSales — Erro", mensagem)
    root.destroy()


def pasta_projeto():
    if getattr(sys, "frozen", False):
        # .exe fica na raiz do projeto (mesma pasta do manage.py)
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def porta_livre(host="127.0.0.1", porta=8000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, porta)) != 0


def aguardar_servidor(host="127.0.0.1", porta=8000, timeout=30):
    inicio = time.time()
    while time.time() - inicio < timeout:
        if not porta_livre(host, porta):
            return True
        time.sleep(0.4)
    return False


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

    # Servidor já está rodando — só abre o navegador
    if not porta_livre():
        webbrowser.open("http://127.0.0.1:8000")
        return

    log_path = projeto / "gsales.log"
    log = open(log_path, "w", encoding="utf-8")

    subprocess.Popen(
        [str(python), str(manage), "runserver", "--noreload"],
        cwd=str(projeto),
        creationflags=subprocess.CREATE_NO_WINDOW,
        stdout=log,
        stderr=log,
    )

    if aguardar_servidor(timeout=60):
        webbrowser.open("http://127.0.0.1:8000")
    else:
        mostrar_erro(
            f"O servidor não respondeu em 60 segundos.\n"
            f"Verifique o arquivo de log:\n{log_path}\n\n"
            f"Ou acesse manualmente: http://127.0.0.1:8000"
        )


if __name__ == "__main__":
    main()
