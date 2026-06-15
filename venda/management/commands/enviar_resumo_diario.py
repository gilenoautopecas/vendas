from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils import timezone

from venda.models import Venda
from core.telegram_utils import enviar_mensagem_telegram


def formatar_real(valor):
    valor = valor or Decimal("0.00")
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


class Command(BaseCommand):
    help = "Envia resumo diário de vendas no Telegram"

    def handle(self, *args, **options):
        hoje = timezone.localdate()

        vendas = Venda.objects.filter(
            data__date=hoje,
            cancelada=False
        )

        total = vendas.aggregate(total=Sum("total"))["total"] or Decimal("0.00")
        quantidade = vendas.count()
        ticket = total / quantidade if quantidade else Decimal("0.00")

        pagamentos = vendas.values("forma_pagamento").annotate(total=Sum("total"))

        dados = {
            "PIX": Decimal("0.00"),
            "CARTAO": Decimal("0.00"),
            "DINHEIRO": Decimal("0.00"),
            "NOTA": Decimal("0.00"),
        }

        for p in pagamentos:
            dados[p["forma_pagamento"]] = p["total"] or Decimal("0.00")

        texto = (
            f"📊 Fechamento do dia\n\n"
            f"Data: {hoje.strftime('%d/%m/%Y')}\n"
            f"💰 Total: {formatar_real(total)}\n"
            f"🧾 Vendas: {quantidade}\n"
            f"📈 Ticket médio: {formatar_real(ticket)}\n\n"
            f"💳 Pagamentos\n"
            f"PIX: {formatar_real(dados['PIX'])}\n"
            f"Cartão: {formatar_real(dados['CARTAO'])}\n"
            f"Dinheiro: {formatar_real(dados['DINHEIRO'])}\n"
            f"Notinha: {formatar_real(dados['NOTA'])}"
        )

        ok = enviar_mensagem_telegram(texto)

        if ok:
            self.stdout.write(self.style.SUCCESS("Resumo diário enviado com sucesso."))
        else:
            self.stdout.write(self.style.ERROR("Falha ao enviar resumo diário."))
