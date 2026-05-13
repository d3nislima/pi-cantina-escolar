import unittest
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.agendamento.models.pedido import ItemPedido, PedidoAntecipado
from apps.estoque.models.movimento import MovimentoEstoque
from apps.estoque.models.produto import Categoria, Produto
from apps.vendas.models.venda import JanelaAtendimento, Venda


def _make_produto(nome="Coxinha", preco=Decimal("5.00")):
    cat, _ = Categoria.objects.get_or_create(nome="Lanche")
    return Produto.objects.create(
        nome=nome, categoria=cat, unidade_medida="un",
        preco_venda=preco, estoque_atual=Decimal("10"),
    )


def _make_janela(nome="Recreio"):
    return JanelaAtendimento.objects.create(
        nome=nome,
        hora_inicio="10:00",
        hora_fim="10:30",
        ativo=True,
    )


def _set_cart(client, produto, quantidade=Decimal("1")):
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


class AgendarPedidoViewTest(TestCase):
    def test_cria_pedido_com_itens(self):
        p = _make_produto()
        j = _make_janela()
        _set_cart(self.client, p)
        self.client.post(reverse("agendamento-novo"), {
            "nome_aluno": "João Silva",
            "turma": "2A",
            "janela_atendimento": j.pk,
        })
        self.assertEqual(PedidoAntecipado.objects.count(), 1)
        pedido = PedidoAntecipado.objects.first()
        self.assertEqual(pedido.nome_aluno, "João Silva")
        self.assertEqual(pedido.turma, "2A")
        self.assertEqual(pedido.status, "pendente")
        self.assertEqual(pedido.itens.count(), 1)

    def test_limpa_carrinho_apos_agendar(self):
        p = _make_produto()
        j = _make_janela()
        _set_cart(self.client, p)
        self.client.post(reverse("agendamento-novo"), {
            "nome_aluno": "Maria",
            "turma": "1B",
            "janela_atendimento": j.pk,
        })
        self.assertEqual(self.client.session["carrinho"], [])

    def test_carrinho_vazio_redireciona_para_venda_create(self):
        session = self.client.session
        session["carrinho"] = []
        session.save()
        j = _make_janela()
        response = self.client.post(reverse("agendamento-novo"), {
            "nome_aluno": "Ana",
            "turma": "3C",
            "janela_atendimento": j.pk,
        })
        self.assertRedirects(response, reverse("venda-create"), fetch_redirect_response=False)

    def test_redireciona_para_agendamento_list(self):
        p = _make_produto()
        j = _make_janela()
        _set_cart(self.client, p)
        response = self.client.post(reverse("agendamento-novo"), {
            "nome_aluno": "Carlos",
            "turma": "2B",
            "janela_atendimento": j.pk,
        })
        self.assertRedirects(response, reverse("agendamento-list"), fetch_redirect_response=False)

    def test_nao_deduz_estoque(self):
        p = _make_produto()
        j = _make_janela()
        _set_cart(self.client, p, quantidade=Decimal("3"))
        estoque_antes = p.estoque_atual
        self.client.post(reverse("agendamento-novo"), {
            "nome_aluno": "Pedro",
            "turma": "1A",
            "janela_atendimento": j.pk,
        })
        p.refresh_from_db()
        self.assertEqual(p.estoque_atual, estoque_antes)


@unittest.skip("template criado na Task 5")
class AgendamentoListViewTest(TestCase):
    def test_lista_ok(self):
        response = self.client.get(reverse("agendamento-list"))
        self.assertEqual(response.status_code, 200)

    def test_exibe_apenas_pendentes(self):
        j = _make_janela()
        PedidoAntecipado.objects.create(
            nome_aluno="Ana", turma="1A", janela_atendimento=j, status="pendente"
        )
        PedidoAntecipado.objects.create(
            nome_aluno="Bruno", turma="2B", janela_atendimento=j, status="retirado"
        )
        response = self.client.get(reverse("agendamento-list"))
        self.assertEqual(len(response.context["pedidos"]), 1)
        self.assertEqual(response.context["pedidos"][0].nome_aluno, "Ana")

    def test_busca_por_nome(self):
        j = _make_janela()
        PedidoAntecipado.objects.create(nome_aluno="Carlos", turma="1A", janela_atendimento=j, status="pendente")
        PedidoAntecipado.objects.create(nome_aluno="Diana", turma="2B", janela_atendimento=j, status="pendente")
        response = self.client.get(reverse("agendamento-list") + "?q=carlos")
        self.assertEqual(len(response.context["pedidos"]), 1)

    def test_busca_por_turma(self):
        j = _make_janela()
        PedidoAntecipado.objects.create(nome_aluno="Eduardo", turma="3C", janela_atendimento=j, status="pendente")
        PedidoAntecipado.objects.create(nome_aluno="Fernanda", turma="1A", janela_atendimento=j, status="pendente")
        response = self.client.get(reverse("agendamento-list") + "?q=3C")
        self.assertEqual(len(response.context["pedidos"]), 1)


class CancelarPedidoViewTest(TestCase):
    def test_cancela_pedido_pendente(self):
        j = _make_janela()
        pedido = PedidoAntecipado.objects.create(
            nome_aluno="Gabi", turma="2A", janela_atendimento=j, status="pendente"
        )
        self.client.post(reverse("agendamento-cancelar", args=[pedido.pk]))
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, "expirado")

    def test_cancela_redireciona_para_list(self):
        j = _make_janela()
        pedido = PedidoAntecipado.objects.create(
            nome_aluno="Hugo", turma="3B", janela_atendimento=j, status="pendente"
        )
        response = self.client.post(reverse("agendamento-cancelar", args=[pedido.pk]))
        self.assertRedirects(response, reverse("agendamento-list"), fetch_redirect_response=False)


class RetiradaPedidoViewTest(TestCase):
    def _make_pedido(self, produto, quantidade=Decimal("2")):
        j = _make_janela()
        pedido = PedidoAntecipado.objects.create(
            nome_aluno="Irene", turma="1C", janela_atendimento=j, status="pendente"
        )
        ItemPedido.objects.create(
            pedido=pedido,
            produto=produto,
            quantidade=quantidade,
            valor_unitario=produto.preco_venda,
        )
        return pedido

    @unittest.skip("template criado na Task 5")
    def test_get_exibe_form(self):
        p = _make_produto()
        pedido = self._make_pedido(p)
        response = self.client.get(reverse("agendamento-retirada", args=[pedido.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "agendamento/retirada_form.html")

    def test_post_cria_venda(self):
        p = _make_produto()
        pedido = self._make_pedido(p)
        self.client.post(reverse("agendamento-retirada", args=[pedido.pk]), {
            "forma_pagamento": "dinheiro",
        })
        self.assertEqual(Venda.objects.count(), 1)

    def test_post_deduz_estoque(self):
        p = _make_produto()
        estoque_antes = p.estoque_atual
        pedido = self._make_pedido(p, quantidade=Decimal("2"))
        self.client.post(reverse("agendamento-retirada", args=[pedido.pk]), {
            "forma_pagamento": "pix",
        })
        p.refresh_from_db()
        self.assertEqual(p.estoque_atual, estoque_antes - Decimal("2"))

    def test_post_cria_movimento_estoque(self):
        p = _make_produto()
        pedido = self._make_pedido(p)
        self.client.post(reverse("agendamento-retirada", args=[pedido.pk]), {
            "forma_pagamento": "dinheiro",
        })
        self.assertEqual(MovimentoEstoque.objects.filter(produto=p, operacao="saida").count(), 1)

    def test_post_marca_pedido_retirado(self):
        p = _make_produto()
        pedido = self._make_pedido(p)
        self.client.post(reverse("agendamento-retirada", args=[pedido.pk]), {
            "forma_pagamento": "dinheiro",
        })
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, "retirado")

    def test_post_redireciona_para_list(self):
        p = _make_produto()
        pedido = self._make_pedido(p)
        response = self.client.post(reverse("agendamento-retirada", args=[pedido.pk]), {
            "forma_pagamento": "cartao",
        })
        self.assertRedirects(response, reverse("agendamento-list"), fetch_redirect_response=False)
