import subprocess

ISQL_PATH = r"C:\Program Files (x86)\Firebird\Firebird_5_0\isql.exe"
DB_PATH = r"C:\GDOOR Sistemas\GDOOR PRO\DATAGES.FDB"


def buscar_produtos_gdoor():

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
            ISQL_PATH,
            "-user", "SYSDBA",
            "-password", "masterkey",
            DB_PATH,
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
            produto["preco_venda"] = linha.replace(
                "PRECO_VENDA",
                "",
                1
            ).strip()

    if produto:
        produtos.append(produto)

    return produtos
