from django import forms
from .models import Venda
from core.models import Produto


class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ["forma_pagamento", "observacao"]
        widgets = {
            "forma_pagamento": forms.Select(attrs={
                "class": "form-select"
            }),
            "observacao": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3, 
                "placeholder": "Observações da venda (opcional)"
            }),
        }



class ItemVendaForm(forms.Form):
    produto = forms.ModelChoiceField(
        queryset=Produto.objects.filter(ativo=True),
        label="Produto"
    )
    quantidade = forms.DecimalField(min_value=0.01)
    preco_unitario = forms.DecimalField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["produto"].queryset = Produto.objects.order_by("nome")
