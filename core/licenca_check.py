"""
Verificador de licença GSales.
A chave pública está embutida aqui — não dá para forjar sem a privada.
"""

import base64
import json
from datetime import date
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.exceptions import InvalidSignature

# Chave pública gerada por licenca/gerar_chaves.py (nunca mude sem regerar todas as licenças)
CHAVE_PUBLICA = '-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEAxpq3oqiOt/X86Xglh2xBM6aq6+8rzqlJJ+GWcYhY4F0=\n-----END PUBLIC KEY-----\n'

LICENCA_PATH = Path(__file__).resolve().parent.parent / "licenca.key"

_chave_publica: Ed25519PublicKey = load_pem_public_key(CHAVE_PUBLICA.encode())


class ResultadoLicenca:
    def __init__(self, valida: bool, motivo: str, cliente: str = "", validade: str = "", dias_restantes: int = 0):
        self.valida = valida
        self.motivo = motivo
        self.cliente = cliente
        self.validade = validade
        self.dias_restantes = dias_restantes


def verificar_licenca() -> ResultadoLicenca:
    if not LICENCA_PATH.exists():
        return ResultadoLicenca(False, "Arquivo licenca.key não encontrado.")

    try:
        conteudo = LICENCA_PATH.read_text(encoding="utf-8").strip()
        partes = conteudo.split(".")
        if len(partes) != 2:
            return ResultadoLicenca(False, "Formato de licença inválido.")

        payload_bytes  = base64.urlsafe_b64decode(partes[0])
        assinatura     = base64.urlsafe_b64decode(partes[1])
    except Exception:
        return ResultadoLicenca(False, "Não foi possível ler a licença.")

    try:
        _chave_publica.verify(assinatura, payload_bytes)
    except InvalidSignature:
        return ResultadoLicenca(False, "Assinatura inválida. Licença corrompida ou falsificada.")

    try:
        dados = json.loads(payload_bytes.decode())
    except Exception:
        return ResultadoLicenca(False, "Dados da licença corrompidos.")

    validade_str = dados.get("validade", "")
    cliente      = dados.get("cliente", "")

    # Licença vitalícia
    if validade_str == "9999-12-31":
        return ResultadoLicenca(True, "OK", cliente=cliente, validade="Vitalícia", dias_restantes=99999)

    try:
        validade_date = date.fromisoformat(validade_str)
    except ValueError:
        return ResultadoLicenca(False, "Data de validade inválida na licença.")

    dias_restantes = (validade_date - date.today()).days

    if dias_restantes < 0:
        return ResultadoLicenca(
            False,
            f"Licença expirada em {validade_date.strftime('%d/%m/%Y')}.",
            cliente=cliente,
            validade=validade_date.strftime("%d/%m/%Y"),
            dias_restantes=0,
        )

    return ResultadoLicenca(
        True, "OK",
        cliente=cliente,
        validade=validade_date.strftime("%d/%m/%Y"),
        dias_restantes=dias_restantes,
    )
