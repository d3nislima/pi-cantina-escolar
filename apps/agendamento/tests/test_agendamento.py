from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.agendamento.models.pedido import ItemPedido, PedidoAntecipado
from apps.estoque.models.produto import Categoria, Produto
from apps.vendas.models.venda import JanelaAtendimento


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
