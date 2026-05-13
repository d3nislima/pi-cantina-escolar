from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from apps.vendas.models.venda import Venda


class VendaListRelatorioTest(TestCase):
    def test_historico_vendas_ok(self):
        response = self.client.get(reverse("venda-list"))
        self.assertEqual(response.status_code, 200)

    def test_historico_vendas_template(self):
        response = self.client.get(reverse("venda-list"))
        self.assertTemplateUsed(response, "vendas/venda_list.html")

    def test_historico_vendas_lista_vendas(self):
        Venda.objects.create(
            forma_pagamento="dinheiro",
            valor_bruto=Decimal("5.00"),
            valor_total=Decimal("5.00"),
            vendido_em=timezone.now(),
        )
        response = self.client.get(reverse("venda-list"))
        self.assertEqual(len(response.context["vendas"]), 1)
