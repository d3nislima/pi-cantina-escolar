from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from apps.estoque.models.produto import Categoria, Produto


def _make_produto(nome="Coxinha", preco=Decimal("5.00")):
    cat, _ = Categoria.objects.get_or_create(nome="Lanche")
    return Produto.objects.create(
        nome=nome, categoria=cat, unidade_medida="un",
        preco_venda=preco, estoque_atual=Decimal("10"),
    )


def _add_to_cart(client, produto, quantidade=Decimal("2")):
    session = client.session
    session["carrinho"] = [{
        "produto_id": produto.pk,
        "nome": produto.nome,
        "preco_unitario": str(produto.preco_venda),
        "quantidade": str(quantidade),
        "subtotal": str(produto.preco_venda * quantidade),
        "unidade_medida": produto.unidade_medida,
    }]
    session.save()


class AjustarQuantidadeViewTest(TestCase):
    def test_mais_incrementa_quantidade(self):
        p = _make_produto()
        _add_to_cart(self.client, p, quantidade=Decimal("2"))
        self.client.post(reverse("venda-ajustar-item"), {"produto_id": p.pk, "acao": "mais"})
        self.assertEqual(Decimal(self.client.session["carrinho"][0]["quantidade"]), Decimal("3"))

    def test_menos_decrementa_quantidade(self):
        p = _make_produto()
        _add_to_cart(self.client, p, quantidade=Decimal("2"))
        self.client.post(reverse("venda-ajustar-item"), {"produto_id": p.pk, "acao": "menos"})
        self.assertEqual(Decimal(self.client.session["carrinho"][0]["quantidade"]), Decimal("1"))

    def test_menos_remove_quando_chega_zero(self):
        p = _make_produto()
        _add_to_cart(self.client, p, quantidade=Decimal("1"))
        self.client.post(reverse("venda-ajustar-item"), {"produto_id": p.pk, "acao": "menos"})
        self.assertEqual(len(self.client.session["carrinho"]), 0)

    def test_ajuste_atualiza_subtotal(self):
        p = _make_produto(preco=Decimal("5.00"))
        _add_to_cart(self.client, p, quantidade=Decimal("2"))
        self.client.post(reverse("venda-ajustar-item"), {"produto_id": p.pk, "acao": "mais"})
        self.assertEqual(Decimal(self.client.session["carrinho"][0]["subtotal"]), Decimal("15.00"))

    def test_redireciona_para_venda_create(self):
        p = _make_produto()
        _add_to_cart(self.client, p)
        response = self.client.post(reverse("venda-ajustar-item"), {"produto_id": p.pk, "acao": "mais"})
        self.assertRedirects(response, reverse("venda-create"))
