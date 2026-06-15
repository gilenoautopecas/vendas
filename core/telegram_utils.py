import requests
from django.conf import settings

TOKEN = "8325809654:AAGUsksqZMTOt1txd5eVdrfqdcktJSh_5BY"
TELEGRAM_CHAT_ID = ["1914515676","8141747252"]


def enviar_mensagem_telegram(texto):
    token = TOKEN
    chat_ids = TELEGRAM_CHAT_ID

    if not token or not chat_ids:
        print("TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_IDS não configurados.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    sucesso = True

    for chat_id in chat_ids:
        payload = {
            "chat_id": chat_id,
            "text": texto,
        }

        try:
            resposta = requests.post(url, data=payload, timeout=15)
            if resposta.status_code != 200:
                print(f"Erro ao enviar para chat_id {chat_id}: {resposta.text}")
                sucesso = False
        except Exception as e:
            print(f"Erro ao enviar para chat_id {chat_id}: {e}")
            sucesso = False

    return sucesso
