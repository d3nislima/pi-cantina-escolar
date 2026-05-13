from decimal import Decimal

from django.db.models import F, Sum
from django.utils import timezone
from django.views.generic import TemplateView

from apps.estoque.models.movimento import MovimentoEstoque
from apps.estoque.models.produto import Categoria, Produto
from apps.vendas.models.venda import ItemVenda, JanelaAtendimento, Venda


class DashboardView(TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoje = timezone.localdate()

        movimentacoes_hoje = MovimentoEstoque.objects.filter(data_movimento__date=hoje)
        vendas_hoje_qs = Venda.objects.filter(vendido_em__date=hoje)

        ctx["entradas_hoje"] = movimentacoes_hoje.filter(operacao="entrada").count()
        ctx["saidas_hoje"] = movimentacoes_hoje.filter(operacao="saida").count()
        ctx["total_produtos"] = Produto.objects.filter(ativo=True).count()
        ctx["produtos_criticos"] = Produto.objects.filter(
            ativo=True,
            estoque_atual__lte=F("estoque_minimo"),
        ).order_by("nome")

        ctx["vendas_hoje"] = vendas_hoje_qs.count()
        ctx["faturado_hoje"] = (
            vendas_hoje_qs.aggregate(total=Sum("valor_total"))["total"] or Decimal("0")
        )
        ctx["ultimas_vendas"] = vendas_hoje_qs.prefetch_related("itens__produto").order_by("-vendido_em")[:5]
        ctx["top_produtos"] = (
            ItemVenda.objects
            .filter(venda__vendido_em__date=hoje)
            .values("produto__nome", "produto__unidade_medida")
            .annotate(total_qty=Sum("quantidade"), total_valor=Sum("valor_total"))
            .order_by("-total_qty")[:5]
        )

        return ctx


class ConfiguracoesView(TemplateView):
    template_name = "configuracoes/configuracoes.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categorias"] = Categoria.objects.select_related("categoria_pai").order_by(
            "categoria_pai__nome", "nome"
        )
        ctx["janelas"] = JanelaAtendimento.objects.order_by("hora_inicio")
        return ctx
