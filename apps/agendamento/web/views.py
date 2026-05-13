from decimal import Decimal

from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from apps.agendamento.models.pedido import ItemPedido, PedidoAntecipado
from apps.estoque.models.movimento import MovimentoEstoque
from apps.estoque.models.produto import Produto
from apps.vendas.models.venda import ItemVenda, JanelaAtendimento, Venda


def _expirar_pedidos_vencidos():
    agora_local = timezone.localtime(timezone.now())
    hoje = agora_local.date()
    hora_atual = agora_local.time()
    PedidoAntecipado.objects.filter(status="pendente").filter(
        Q(data_atendimento__lt=hoje)
        | Q(data_atendimento=hoje, janela_atendimento__hora_fim__lt=hora_atual)
    ).update(status="expirado")


class AgendamentoListView(View):
    template_name = "agendamento/agendamento_list.html"

    def get(self, request):
        _expirar_pedidos_vencidos()
        q = request.GET.get("q", "").strip()
        pedidos = PedidoAntecipado.objects.filter(status="pendente").select_related(
            "janela_atendimento"
        ).prefetch_related("itens__produto")
        if q:
            pedidos = pedidos.filter(
                Q(nome_aluno__icontains=q) | Q(turma__icontains=q)
            )
        janelas = JanelaAtendimento.objects.filter(ativo=True)
        return render(request, self.template_name, {"pedidos": pedidos, "q": q, "janelas": janelas})


class AgendarPedidoView(View):
    def post(self, request):
        carrinho = request.session.get("carrinho", [])
        if not carrinho:
            return redirect("venda-create")

        from datetime import date as date_type
        nome_aluno = request.POST.get("nome_aluno", "").strip()
        turma = request.POST.get("turma", "").strip()
        janela_id = request.POST.get("janela_atendimento")
        data_str = request.POST.get("data_atendimento", "").strip()

        try:
            janela = JanelaAtendimento.objects.get(pk=janela_id)
        except JanelaAtendimento.DoesNotExist:
            return redirect("venda-create")

        try:
            data_atendimento = date_type.fromisoformat(data_str) if data_str else date_type.today()
        except ValueError:
            data_atendimento = date_type.today()

        pedido = PedidoAntecipado.objects.create(
            nome_aluno=nome_aluno,
            turma=turma,
            data_atendimento=data_atendimento,
            janela_atendimento=janela,
            status="pendente",
        )

        for item in carrinho:
            ItemPedido.objects.create(
                pedido=pedido,
                produto=Produto.objects.get(pk=item["produto_id"]),
                quantidade=Decimal(str(item["quantidade"])),
                valor_unitario=Decimal(str(item["preco_unitario"])),
            )

        request.session["carrinho"] = []
        return redirect("agendamento-list")


class RetiradaPedidoView(View):
    template_name = "agendamento/retirada_form.html"

    def get(self, request, pk):
        pedido = get_object_or_404(PedidoAntecipado, pk=pk, status="pendente")
        return render(request, self.template_name, {
            "pedido": pedido,
            "formas_pagamento": Venda.PAGAMENTO_CHOICES,
        })

    def post(self, request, pk):
        pedido = get_object_or_404(PedidoAntecipado, pk=pk, status="pendente")
        forma_pagamento = request.POST.get("forma_pagamento")
        valor_recebido = request.POST.get("valor_recebido") or None

        itens = list(pedido.itens.select_related("produto").all())
        valor_total = sum(item.valor_total for item in itens)
        troco = None
        if valor_recebido and forma_pagamento == "dinheiro":
            troco = Decimal(str(valor_recebido)) - valor_total

        venda = Venda.objects.create(
            forma_pagamento=forma_pagamento,
            janela_atendimento=pedido.janela_atendimento,
            modo_atendimento="pedido_antecipado",
            valor_bruto=valor_total,
            valor_total=valor_total,
            valor_recebido=Decimal(str(valor_recebido)) if valor_recebido else None,
            troco=troco,
            vendido_em=timezone.now(),
        )

        for item in itens:
            produto = item.produto
            ItemVenda.objects.create(
                venda=venda,
                produto=produto,
                quantidade=item.quantidade,
                valor_unitario=item.valor_unitario,
                valor_total=item.valor_total,
            )
            MovimentoEstoque.objects.create(
                produto=produto,
                operacao="saida",
                origem="venda",
                quantidade=item.quantidade,
                valor_unitario=item.valor_unitario,
                saldo_antes=produto.estoque_atual,
                saldo_depois=produto.estoque_atual - item.quantidade,
                data_movimento=venda.vendido_em,
            )
            produto.estoque_atual -= item.quantidade
            produto.save()

        pedido.status = "retirado"
        pedido.save(update_fields=["status", "atualizado_em"])
        return redirect("agendamento-list")


class CancelarPedidoView(View):
    def post(self, request, pk):
        pedido = get_object_or_404(PedidoAntecipado, pk=pk, status="pendente")
        pedido.status = "expirado"
        pedido.save(update_fields=["status", "atualizado_em"])
        return redirect("agendamento-list")
