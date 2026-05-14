from decimal import Decimal

from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from apps.agendamento.models.pedido import ItemPedido, PedidoAntecipado
from apps.estoque.models.produto import Produto
from apps.vendas.models.venda import ItemVenda, JanelaAtendimento, Venda
from apps.vendas.services import EstoqueInsuficienteError, realizar_venda


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
    """
    Usa realizar_venda() do service, exatamente como a venda direta.
    Garante que pedido antecipado também valida estoque no momento da retirada.
    """
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
        valor_recebido_raw = request.POST.get("valor_recebido") or None
        valor_recebido = Decimal(str(valor_recebido_raw)) if valor_recebido_raw else None

        # Monta carrinho no formato esperado pelo service
        itens_carrinho = [
            {
                "produto_id": item.produto_id,
                "quantidade": str(item.quantidade),
                "preco_unitario": str(item.valor_unitario),
                "subtotal": str(item.valor_total),
            }
            for item in pedido.itens.select_related("produto").all()
        ]

        try:
            realizar_venda(
                itens_carrinho=itens_carrinho,
                forma_pagamento=forma_pagamento,
                modo_atendimento="pedido_antecipado",
                janela=pedido.janela_atendimento,
                valor_recebido=valor_recebido,
            )
        except EstoqueInsuficienteError as e:
            erro = (
                f"Não foi possível retirar o pedido: estoque insuficiente para "
                f"'{e.produto_nome}' (disponível: {e.disponivel} un., solicitado: {e.solicitado} un.)."
            )
            return render(request, self.template_name, {
                "pedido": pedido,
                "formas_pagamento": Venda.PAGAMENTO_CHOICES,
                "erro": erro,
            })

        pedido.status = "retirado"
        pedido.save(update_fields=["status", "atualizado_em"])
        return redirect("agendamento-list")


class CancelarPedidoView(View):
    def post(self, request, pk):
        pedido = get_object_or_404(PedidoAntecipado, pk=pk, status="pendente")
        pedido.status = "expirado"
        pedido.save(update_fields=["status", "atualizado_em"])
        return redirect("agendamento-list")
