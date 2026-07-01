"""
Agente local de sincronização Gdoor -> servidor web central.

Roda na máquina onde o Gdoor está instalado (mesma rede do Firebird).
Lê os produtos direto do banco .FDB via isql.exe e envia para a API
do sistema web central, autenticado pelo token da empresa.

Configuração: edite o arquivo config.ini (mesma pasta deste script).
"""

import configparser
import subprocess
import sys
from pathlib import Path

import requests


def pasta_base():
    """Pasta onde o .exe (ou o script) está, mesmo quando empacotado pelo PyInstaller."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


CONFIG_PATH = pasta_base() / "config.ini"
CONFIG_EXEMPLO = """[gdoor]
isql_path = C:\\Program Files (x86)\\Firebird\\Firebird_5_0\\isql.exe
db_path = C:\\GDOOR Sistemas\\GDOOR PRO\\DATAGES.FDB
db_user = SYSDBA
db_password = masterkey

[servidor]
url = https://seu-sistema.exemplo.com
token = COLE_AQUI_O_TOKEN_DA_EMPRESA
"""


def carregar_config():
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(CONFIG_EXEMPLO, encoding="utf-8")
        raise SystemExit(
            f"Arquivo config.ini não encontrado. Um modelo foi criado em:\n{CONFIG_PATH}\n"
            "Edite-o com os dados da sua empresa e rode o agente novamente."
        )

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding="utf-8")

    return {
        "isql_path": config.get("gdoor", "isql_path"),
        "db_path": config.get("gdoor", "db_path"),
        "db_user": config.get("gdoor", "db_user", fallback="SYSDBA"),
        "db_password": config.get("gdoor", "db_password", fallback="masterkey"),
        "servidor_url": config.get("servidor", "url"),
        "token": config.get("servidor", "token"),
    }


def buscar_produtos_gdoor(cfg):
    sql = """
    SET HEADING OFF;
    SET LIST ON;

    SELECT
        CODIGO,
        DESCRICAO,
        PRECO_VENDA
    FROM ESTOQUE;

    QUIT;
    """

    resultado = subprocess.run(
        [
            cfg["isql_path"],
            "-user", cfg["db_user"],
            "-password", cfg["db_password"],
            cfg["db_path"],
        ],
        input=sql,
        text=True,
        capture_output=True,
        encoding="latin1"
    )

    produtos = []
    produto = {}

    for linha in resultado.stdout.splitlines():
        linha = linha.strip()

        if not linha:
            if produto:
                produtos.append(produto)
                produto = {}
            continue

        if linha.startswith("CODIGO"):
            produto["codigo"] = linha.replace("CODIGO", "", 1).strip()
        elif linha.startswith("DESCRICAO"):
            produto["descricao"] = linha.replace("DESCRICAO", "", 1).strip()
        elif linha.startswith("PRECO_VENDA"):
            produto["preco_venda"] = linha.replace("PRECO_VENDA", "", 1).strip()

    if produto:
        produtos.append(produto)

    return produtos


def enviar_para_servidor(cfg, produtos):
    resposta = requests.post(
        cfg["servidor_url"].rstrip("/") + "/core/sync-produtos/",
        json={"produtos": produtos},
        headers={"Authorization": f"Token {cfg['token']}"},
        timeout=30,
    )
    resposta.raise_for_status()
    return resposta.json()


def main():
    cfg = carregar_config()

    print("Lendo produtos do Gdoor...")
    produtos = buscar_produtos_gdoor(cfg)
    print(f"{len(produtos)} produtos encontrados no Gdoor.")

    print("Enviando para o servidor central...")
    resultado = enviar_para_servidor(cfg, produtos)
    print(f"Sincronização concluída: {resultado.get('importados', 0)} produtos importados.")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        print(e)
    except Exception as e:
        print(f"Erro ao sincronizar: {e}")
    finally:
        if getattr(sys, "frozen", False):
            input("\nPressione ENTER para fechar...")
