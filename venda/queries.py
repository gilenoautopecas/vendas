from django.db.models import Sum, Count
from django.db.models.functions import TruncDay, TruncMonth, TruncYear, TruncWeek
from django.utils.timezone import now
from .models import Venda, ItemVenda
from django.db.models import Q


def total_hoje():
    hoje = now().date()

    return Venda.objects.filter(
        data__date=hoje,
        cancelada=False
    ).aggregate(
        total=Sum("total")
    )["total"] or 0


def total_semana():
    return (
        Venda.objects
        .annotate(semana=TruncWeek("data"))
        .values("semana")
        .annotate(total=Sum("total"))
        .order_by("-semana")
        .first()
    )


def total_por_mes():
    return (
        Venda.objects
        .filter(cancelada=False)
        .annotate(mes=TruncMonth("data"))
        .values("mes")
        .annotate(total=Sum("total"))
        .order_by("mes")
    )


def total_por_ano():
    return (
        Venda.objects
        .filter(cancelada=False)
        .annotate(ano=TruncYear("data"))
        .values("ano")
        .annotate(total=Sum("total"))
        .order_by("ano")
    )


def produtos_mais_vendidos():
    return (
        ItemVenda.objects
        .values("produto__nome")
        .annotate(total_vendido=Sum("quantidade"))
        .order_by("-total_vendido")
    )


def ticket_medio():
    resultado = Venda.objects.filter(
        cancelada=False
    ).aggregate(
        total=Sum("total"),
        quantidade=Count("id")
    )

    if resultado["quantidade"] == 0:
        return 0

    return resultado["total"] / resultado["quantidade"]


def total_por_periodo(data_inicio, data_fim):
    return Venda.objects.filter(
        data__date__range=[data_inicio, data_fim],
        cancelada=False
    ).aggregate(
        total=Sum("total")
    )["total"] or 0


def listar_vendas_filtradas(empresa, q=None, data=None, inicio=None, fim=None, limit=100):
    qs = Venda.objects.filter(empresa=empresa, cancelada=False).order_by("-data")

    if not data and not (inicio and fim):
        qs = qs.filter(data__date=now().date())

    if data:
        qs = qs.filter(data__date=data)

    if inicio and fim:
        qs = qs.filter(data__date__range=[inicio, fim])

    if q:
        qs = qs.filter(
            Q(id__icontains=q) |
            Q(forma_pagamento__icontains=q) |
            Q(observacao__icontains=q) |
            Q(itens__produto__nome__icontains=q)
        ).distinct()

    return qs


def vendas_por_dia(empresa, inicio, fim):
    return (
        Venda.objects.filter(
            empresa=empresa,
            cancelada=False,
            data__date__range=[inicio, fim]
        )
        .annotate(dia=TruncDay("data"))
        .values("dia")
        .annotate(
            total=Sum("total"),
            quantidade=Count("id")
        )
        .order_by("dia")
    )
