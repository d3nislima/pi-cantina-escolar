from decimal import Decimal

from django.test import TestCase

from apps.estoque.models.produto import Categoria, Produto
from apps.estoque.web.forms import MovimentacaoSimplificadaForm


def _make_produto():
    cat = Categoria.objects.create(nome="Teste")
    return Produto.objects.create(
        nome="Produto Teste",
        categoria=cat,
        unidade_medida="un",
        preco_venda=Decimal("5.00"),
    )


class MovimentacaoSimplificadaFormTest(TestCase):
    def setUp(self):
        self.produto = _make_produto()

    def _valid_data(self, **overrides):
        data = {
            "produto": self.produto.pk,
            "origem": "compra",
            "quantidade": "10",
            "valor_unitario": "",
            "observacao": "",
        }
        data.update(overrides)
        return data

    def test_valid_form_compra(self):
        form = MovimentacaoSimplificadaForm(self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_form_perda_sem_valor(self):
        form = MovimentacaoSimplificadaForm(self._valid_data(origem="perda"))
        self.assertTrue(form.is_valid(), form.errors)

    def test_quantidade_zero_invalida(self):
        form = MovimentacaoSimplificadaForm(self._valid_data(quantidade="0"))
        self.assertFalse(form.is_valid())
        self.assertIn("quantidade", form.errors)

    def test_quantidade_negativa_invalida(self):
        form = MovimentacaoSimplificadaForm(self._valid_data(quantidade="-1"))
        self.assertFalse(form.is_valid())
        self.assertIn("quantidade", form.errors)

    def test_produto_obrigatorio(self):
        data = self._valid_data()
        data["produto"] = ""
        form = MovimentacaoSimplificadaForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("produto", form.errors)

    def test_origem_invalida(self):
        form = MovimentacaoSimplificadaForm(self._valid_data(origem="venda"))
        self.assertFalse(form.is_valid())
        self.assertIn("origem", form.errors)

    def test_valor_unitario_opcional(self):
        form = MovimentacaoSimplificadaForm(self._valid_data(valor_unitario=""))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.cleaned_data["valor_unitario"])

    def test_valor_unitario_negativo_invalido(self):
        form = MovimentacaoSimplificadaForm(self._valid_data(valor_unitario="-1"))
        self.assertFalse(form.is_valid())
        self.assertIn("valor_unitario", form.errors)
