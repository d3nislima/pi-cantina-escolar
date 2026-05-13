from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.estoque.models.movimento import MovimentoEstoque
from apps.estoque.models.produto import Categoria, Produto


def _make_produto(nome="Produto A", estoque=Decimal("10")):
    cat, _ = Categoria.objects.get_or_create(nome="Cat")
    p = Produto.objects.create(
        nome=nome,
        categoria=cat,
        unidade_medida="un",
        preco_venda=Decimal("5.00"),
        estoque_atual=estoque,
    )
    return p


class EntradaEstoqueViewGetTest(TestCase):
    def test_get_modo_existente(self):
        url = reverse("entrada-estoque") + "?modo=existente"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["modo"], "existente")

    def test_get_modo_novo(self):
        url = reverse("entrada-estoque") + "?modo=novo"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["modo"], "novo")

    def test_get_modo_padrao_existente(self):
        url = reverse("entrada-estoque")
        response = self.client.get(url)
        self.assertEqual(response.context["modo"], "existente")


class EntradaEstoqueViewPostExistenteTest(TestCase):
    def setUp(self):
        self.produto = _make_produto()
        self.url = reverse("entrada-estoque")

    def test_post_compra_aumenta_estoque(self):
        data = {
            "modo": "existente",
            "produto": self.produto.pk,
            "origem": "compra",
            "quantidade": "5",
            "valor_unitario": "",
            "observacao": "",
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse("produto-list"))
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque_atual, Decimal("15"))

    def test_post_perda_diminui_estoque(self):
        data = {
            "modo": "existente",
            "produto": self.produto.pk,
            "origem": "perda",
            "quantidade": "3",
            "valor_unitario": "",
            "observacao": "",
        }
        self.client.post(self.url, data)
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque_atual, Decimal("7"))

    def test_post_inventario_ajusta_estoque(self):
        data = {
            "modo": "existente",
            "produto": self.produto.pk,
            "origem": "inventario",
            "quantidade": "20",
            "valor_unitario": "",
            "observacao": "",
        }
        self.client.post(self.url, data)
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque_atual, Decimal("20"))

    def test_post_compra_cria_movimento(self):
        data = {
            "modo": "existente",
            "produto": self.produto.pk,
            "origem": "compra",
            "quantidade": "5",
            "valor_unitario": "2.50",
            "observacao": "nota 001",
        }
        self.client.post(self.url, data)
        mov = MovimentoEstoque.objects.filter(produto=self.produto).latest("data_movimento")
        self.assertEqual(mov.operacao, "entrada")
        self.assertEqual(mov.origem, "compra")
        self.assertEqual(mov.quantidade, Decimal("5"))
        self.assertEqual(mov.saldo_antes, Decimal("10"))
        self.assertEqual(mov.saldo_depois, Decimal("15"))

    def test_post_compra_atualiza_preco_custo(self):
        data = {
            "modo": "existente",
            "produto": self.produto.pk,
            "origem": "compra",
            "quantidade": "5",
            "valor_unitario": "3.00",
            "observacao": "",
        }
        self.client.post(self.url, data)
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.preco_custo, Decimal("3.00"))

    def test_post_form_invalido_renderiza_form(self):
        data = {"modo": "existente", "produto": "", "origem": "compra", "quantidade": "5"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)


class EntradaEstoqueViewPostNovoTest(TestCase):
    def setUp(self):
        cat = Categoria.objects.create(nome="CatNova")
        self.cat_pk = cat.pk
        self.url = reverse("entrada-estoque")

    def _novo_produto_data(self, **overrides):
        data = {
            "modo": "novo",
            "nome": "Produto Novo",
            "codigo_barras": "",
            "categoria": self.cat_pk,
            "unidade_medida": "un",
            "preco_venda": "5.00",
            "estoque_minimo": "0",
            "ativo": "on",
            "destaque": "",
            "quantidade_inicial": "10",
            "origem": "compra",
            "valor_unitario": "",
        }
        data.update(overrides)
        return data

    def test_post_novo_cria_produto(self):
        response = self.client.post(self.url, self._novo_produto_data())
        self.assertRedirects(response, reverse("produto-list"))
        self.assertTrue(Produto.objects.filter(nome="Produto Novo").exists())

    def test_post_novo_define_estoque_inicial(self):
        self.client.post(self.url, self._novo_produto_data())
        produto = Produto.objects.get(nome="Produto Novo")
        self.assertEqual(produto.estoque_atual, Decimal("10"))

    def test_post_novo_sem_quantidade_inicial(self):
        self.client.post(self.url, self._novo_produto_data(quantidade_inicial=""))
        produto = Produto.objects.get(nome="Produto Novo")
        self.assertEqual(produto.estoque_atual, Decimal("0"))
        self.assertFalse(MovimentoEstoque.objects.filter(produto=produto).exists())

    def test_post_novo_cria_movimento(self):
        self.client.post(self.url, self._novo_produto_data())
        produto = Produto.objects.get(nome="Produto Novo")
        mov = MovimentoEstoque.objects.get(produto=produto)
        self.assertEqual(mov.operacao, "entrada")
        self.assertEqual(mov.origem, "compra")
        self.assertEqual(mov.saldo_antes, Decimal("0"))
        self.assertEqual(mov.saldo_depois, Decimal("10"))
