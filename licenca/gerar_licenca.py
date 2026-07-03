"""
Gerador de licença GSales.

Uso:
    python licenca/gerar_licenca.py

Vai pedir interativamente: nome do cliente, CNPJ e dias de validade.
Gera o arquivo licenca.key na pasta atual.

Exemplos de dias:
    30      → 1 mês
    90      → 3 meses
    120     → 4 meses (pagamento adiantado)
    365     → 1 ano
    99999   → acesso vitalício / sem expiração
"""

import base64
import json
from datetime import date, timedelta
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key

CHAVE_PRIVADA_PATH = Path(__file__).parent / "privada.pem"

if not CHAVE_PRIVADA_PATH.exists():
    print("Chave privada não encontrada. Rode primeiro: python licenca/gerar_chaves.py")
    exit(1)

chave: Ed25519PrivateKey = load_pem_private_key(
    CHAVE_PRIVADA_PATH.read_bytes(), password=None
)

print("=" * 50)
print("       GERADOR DE LICENÇA GSALES")
print("=" * 50)

cliente = input("Nome do cliente: ").strip()
cnpj    = input("CNPJ (qualquer formato): ").strip()
dias    = input("Dias de validade [30]: ").strip() or "30"
dias    = int(dias)

if dias >= 99999:
    validade_str = "9999-12-31"
    print(f"\n→ Licença VITALÍCIA gerada para {cliente}")
else:
    validade = date.today() + timedelta(days=dias)
    validade_str = validade.isoformat()
    print(f"\n→ Validade: {validade.strftime('%d/%m/%Y')} ({dias} dias)")

payload = json.dumps({
    "cliente": cliente,
    "cnpj": cnpj,
    "dias": dias,
    "validade": validade_str,
}, ensure_ascii=False, separators=(",", ":"))

payload_bytes  = payload.encode()
assinatura     = chave.sign(payload_bytes)

payload_b64    = base64.urlsafe_b64encode(payload_bytes).decode()
assinatura_b64 = base64.urlsafe_b64encode(assinatura).decode()

conteudo = f"{payload_b64}.{assinatura_b64}"

saida = Path("licenca.key")
saida.write_text(conteudo, encoding="utf-8")

print(f"✔ Arquivo salvo: {saida.resolve()}")
print(f"  Cliente : {cliente}")
print(f"  CNPJ    : {cnpj}")
print(f"  Validade: {validade_str}")
print("\nEnvie o arquivo licenca.key para o cliente (WhatsApp, email, etc.)")
print("O cliente deve colocar na pasta raiz do sistema (onde está o manage.py).")
