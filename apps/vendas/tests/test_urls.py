from django.test import TestCase
from django.urls import reverse


class VendasUrlsTest(TestCase):
    def test_venda_create_resolve_para_slash_vendas(self):
        url = reverse("venda-create")
        self.assertEqual(url, "/vendas/")

    def test_venda_list_resolve_para_relatorios(self):
        url = reverse("venda-list")
        self.assertEqual(url, "/relatorios/vendas/")

    def test_nova_venda_get_ok(self):
        response = self.client.get(reverse("venda-create"))
        self.assertEqual(response.status_code, 200)
