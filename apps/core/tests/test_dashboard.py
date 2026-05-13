from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.estoque.models.produto import Categoria, Produto
from apps.vendas.models.venda import ItemVenda, Venda


def _make_produto(nome="Coxinha", preco=Decimal("5.00")):
    cat, _ = Categoria.objects.get_or_create(nome="Lanche")
    return Produto.objects.create(
        nome=nome,
        categoria=cat,
        unidade_medida="un",
        preco_venda=preco,
        estoque_atual=Decimal("10"),
    )


def _make_venda(produto, quantidade=Decimal("1"), forma="dinheiro"):
    venda = Venda.objects.create(
        forma_pagamento=forma,
        valor_bruto=produto.preco_venda * quantidade,
        valor_total=produto.preco_venda * quantidade,
        vendido_em=timezone.now(),
    )
    ItemVenda.objects.create(
        venda=venda,
        produto=produto,
        quantidade=quantidade,
        valor_unitario=produto.preco_venda,
        valor_total=produto.preco_venda * quantidade,
    )
    return venda


class DashboardViewTest(TestCase):
    def test_dashboard_ok(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_vendas_hoje_zero_sem_vendas(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.context["vendas_hoje"], 0)

    def test_faturado_hoje_zero_sem_vendas(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.context["faturado_hoje"], Decimal("0"))

    def test_vendas_hoje_conta_vendas_do_dia(self):
        p = _make_produto()
        _make_venda(p)
        _make_venda(p)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.context["vendas_hoje"], 2)

    def test_faturado_hoje_soma_valor_total(self):
        p = _make_produto(preco=Decimal("5.00"))
        _make_venda(p, quantidade=Decimal("2"))
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.context["faturado_hoje"], Decimal("10.00"))

    def test_ultimas_vendas_max_5(self):
        p = _make_produto()
        for _ in range(7):
            _make_venda(p)
        response = self.client.get(reverse("dashboard"))
        self.assertLessEqual(len(response.context["ultimas_vendas"]), 5)

    def test_top_produtos_max_5(self):
        for i in range(7):
            p = _make_produto(nome=f"Produto {i}")
            _make_venda(p)
        response = self.client.get(reverse("dashboard"))
        self.assertLessEqual(len(response.context["top_produtos"]), 5)

    def test_top_produtos_ordenado_por_quantidade(self):
        p1 = _make_produto(nome="Mais vendido")
        p2 = _make_produto(nome="Menos vendido")
        _make_venda(p1, quantidade=Decimal("3"))
        _make_venda(p2, quantidade=Decimal("1"))
        response = self.client.get(reverse("dashboard"))
        top = list(response.context["top_produtos"])
        self.assertEqual(top[0]["produto__nome"], "Mais vendido")

    def test_ultimas_vendas_ignora_outros_dias(self):
        p = _make_produto()
        ontem = timezone.now() - timedelta(days=1)
        Venda.objects.create(
            forma_pagamento="dinheiro",
            valor_bruto=p.preco_venda,
            valor_total=p.preco_venda,
            vendido_em=ontem,
        )
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(len(response.context["ultimas_vendas"]), 0)

    def test_vendas_hoje_ignora_outros_dias(self):
        p = _make_produto()
        ontem = timezone.now() - timedelta(days=1)
        Venda.objects.create(
            forma_pagamento="dinheiro",
            valor_bruto=p.preco_venda,
            valor_total=p.preco_venda,
            vendido_em=ontem,
        )
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.context["vendas_hoje"], 0)
