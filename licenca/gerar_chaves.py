"""
Gerador de par de chaves Ed25519 para o sistema de licença GSales.

Execute UMA VEZ na sua máquina:
    python licenca/gerar_chaves.py

Guarda:
  - licenca/privada.pem  → NUNCA compartilhe, nunca suba pro git
  - Imprime a chave pública que deve ser colada em core/licenca_check.py
"""

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, PublicFormat, NoEncryption
)
from pathlib import Path

CHAVE_PRIVADA_PATH = Path(__file__).parent / "privada.pem"

if CHAVE_PRIVADA_PATH.exists():
    print("ATENÇÃO: privada.pem já existe. Apague manualmente se quiser gerar uma nova.")
    print("Gerando nova chave iria invalidar TODAS as licenças existentes.")
    exit(1)

chave = Ed25519PrivateKey.generate()

# Salva chave privada
CHAVE_PRIVADA_PATH.write_bytes(
    chave.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
)
print(f"Chave privada salva em: {CHAVE_PRIVADA_PATH}")
print("⚠️  Guarde esse arquivo em local seguro. Nunca suba pro Git.")
print()

# Exibe chave pública para embutir no Django
chave_publica_bytes = chave.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
chave_publica_str = chave_publica_bytes.decode()

print("=" * 60)
print("Cole o valor abaixo em core/licenca_check.py → CHAVE_PUBLICA:")
print("=" * 60)
print(repr(chave_publica_str))
