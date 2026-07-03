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


def pasta_projeto():
    """Pasta raiz do projeto (onde está manage.py)."""
    if getattr(sys, "frozen", False):
        # Rodando como .exe — o launcher fica em launcher\ dentro do projeto
        return Path(sys.executable).resolve().parent.parent
    return Path(__file__).resolve().parent.parent


def porta_disponivel(host="127.0.0.1", porta=8000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, porta)) != 0


def aguardar_servidor(host="127.0.0.1", porta=8000, timeout=30):
    inicio = time.time()
    while time.time() - inicio < timeout:
        if not porta_disponivel(host, porta):
            return True
        time.sleep(0.4)
    return False


def main():
    projeto = pasta_projeto()
    python  = projeto / "venv" / "Scripts" / "python.exe"
    manage  = projeto / "manage.py"

    if not python.exists():
        input(f"[ERRO] Python do venv não encontrado em:\n{python}\n\nPressione ENTER para fechar...")
        return

    if not manage.exists():
        input(f"[ERRO] manage.py não encontrado em:\n{manage}\n\nPressione ENTER para fechar...")
        return

    # Se já tem algo rodando na 8000, só abre o navegador
    if not porta_disponivel():
        webbrowser.open("http://127.0.0.1:8000")
        return

    processo = subprocess.Popen(
        [str(python), str(manage), "runserver", "--noreload"],
        cwd=str(projeto),
        creationflags=subprocess.CREATE_NO_WINDOW,  # sem janela preta
    )

    print("Iniciando GSales", end="", flush=True)
    if aguardar_servidor():
        print(" OK")
        webbrowser.open("http://127.0.0.1:8000")
    else:
        print("\n[AVISO] Servidor demorou para responder. Tente abrir http://127.0.0.1:8000 manualmente.")

    try:
        processo.wait()
    except KeyboardInterrupt:
        processo.terminate()


if __name__ == "__main__":
    main()
