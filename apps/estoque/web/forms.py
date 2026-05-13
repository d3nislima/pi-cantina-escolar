from decimal import Decimal

from django import forms

from apps.estoque.models.movimento import MovimentoEstoque
from apps.estoque.models.produto import Categoria, Produto


class ProdutoForm(forms.ModelForm):
    ORIGEM_CHOICES = [
        ("compra", "Compra"),
        ("doacao", "Doação"),
    ]

    quantidade_inicial = forms.DecimalField(
        required=False,
        min_value=Decimal("0"),
        label="Quantidade inicial",
        help_text="Deixe em branco para começar com estoque 0.",
        widget=forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
    )
    origem = forms.ChoiceField(
        choices=ORIGEM_CHOICES,
        label="Origem da entrada inicial",
        initial="compra",
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    valor_unitario = forms.DecimalField(
        required=False,
        min_value=Decimal("0"),
        label="Valor Unitário",
        help_text="Opcional. Custo unitário da entrada inicial.",
        widget=forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
    )

    class Meta:
        model = Produto
        fields = [
            "nome",
            "codigo_barras",
            "categoria",
            "unidade_medida",
            "preco_venda",
            "estoque_minimo",
            "ativo",
            "destaque",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoria"].queryset = Categoria.objects.filter(ativo=True).order_by("nome")
        for name, field in self.fields.items():
            if name not in ("quantidade_inicial", "origem", "valor_unitario"):
                field.widget.attrs["class"] = "form-input"
        if self.instance.pk:
            del self.fields["quantidade_inicial"]
            del self.fields["origem"]
            del self.fields["valor_unitario"]


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nome", "categoria_pai", "descricao"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoria_pai"].queryset = Categoria.objects.filter(
            categoria_pai__isnull=True, ativo=True
        ).order_by("nome")
        self.fields["categoria_pai"].required = False
        self.fields["descricao"].required = False
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-input"


class MovimentoEstoqueForm(forms.ModelForm):
    class Meta:
        model = MovimentoEstoque
        fields = [
            "produto",
            "operacao",
            "origem",
            "quantidade",
            "valor_unitario",
            "documento_referencia",
            "observacao",
        ]

    ORIGENS_POR_OPERACAO = {
        "entrada": {"compra", "doacao"},
        "saida": {"venda", "perda"},
        "ajuste": {"inventario", "ajuste_manual"},
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["produto"].queryset = Produto.objects.filter(ativo=True).order_by("nome")
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-input"

    def clean(self):
        cleaned_data = super().clean()
        operacao = cleaned_data.get("operacao")
        origem = cleaned_data.get("origem")

        if operacao and origem:
            origens_validas = self.ORIGENS_POR_OPERACAO.get(operacao, set())
            if origem not in origens_validas:
                self.add_error(
                    "origem",
                    f"Origem inválida para operação '{operacao}'. "
                    f"Válidas: {', '.join(sorted(origens_validas))}.",
                )

        return cleaned_data


class MovimentacaoSimplificadaForm(forms.Form):
    ORIGEM_CHOICES = [
        ("compra", "Compra"),
        ("doacao", "Doação"),
        ("perda", "Perda"),
        ("inventario", "Inventário"),
        ("ajuste_manual", "Ajuste Manual"),
    ]

    produto = forms.ModelChoiceField(
        queryset=Produto.objects.filter(ativo=True).order_by("nome"),
        label="Produto",
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    origem = forms.ChoiceField(
        choices=ORIGEM_CHOICES,
        label="Origem",
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    quantidade = forms.DecimalField(
        min_value=Decimal("0.01"),
        label="Quantidade",
        widget=forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
    )
    valor_unitario = forms.DecimalField(
        required=False,
        min_value=Decimal("0"),
        label="Valor Unitário",
        help_text="Opcional. Usado para atualizar custo quando origem for Compra.",
        widget=forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
    )
    observacao = forms.CharField(
        required=False,
        max_length=255,
        label="Observação",
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
