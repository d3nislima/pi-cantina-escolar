from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.estoque.models.produto import Categoria, Produto


def _make_produto(nome, estoque=Decimal("10")):
    cat, _ = Categoria.objects.get_or_create(nome="Lanche")
    return Produto.objects.create(
        nome=nome,
        categoria=cat,
        unidade_medida="un",
        preco_venda=Decimal("5.00"),
        estoque_atual=estoque,
    )


class EstoqueListViewBuscaTest(TestCase):
    def setUp(self):
        _make_produto("Coxinha")
        _make_produto("Suco de Laranja")
        _make_produto("Pão de Queijo")

    def test_sem_q_retorna_todos(self):
        response = self.client.get(reverse("produto-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["produtos"]), 3)

    def test_busca_retorna_correspondentes(self):
        response = self.client.get(reverse("produto-list") + "?q=coxinha")
        self.assertEqual(len(response.context["produtos"]), 1)
        self.assertEqual(response.context["produtos"][0].nome, "Coxinha")

    def test_busca_case_insensitive(self):
        response = self.client.get(reverse("produto-list") + "?q=SUCO")
        self.assertEqual(len(response.context["produtos"]), 1)

    def test_busca_sem_resultado(self):
        response = self.client.get(reverse("produto-list") + "?q=xyz")
        self.assertEqual(len(response.context["produtos"]), 0)

    def test_q_no_contexto(self):
        response = self.client.get(reverse("produto-list") + "?q=pao")
        self.assertEqual(response.context["q"], "pao")

    def test_q_vazio_no_contexto_sem_parametro(self):
        response = self.client.get(reverse("produto-list"))
        self.assertEqual(response.context["q"], "")
