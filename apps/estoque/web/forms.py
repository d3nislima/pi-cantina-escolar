from django import forms

from apps.estoque.models.movimento import MovimentoEstoque
from apps.estoque.models.produto import Categoria, Produto


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            "nome",
            "codigo_barras",
            "categoria",
            "unidade_medida",
            "preco_custo",
            "preco_venda",
            "estoque_minimo",
            "ativo",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoria"].queryset = Categoria.objects.order_by("nome")
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
