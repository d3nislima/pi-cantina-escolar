from django.db.models import F
from django.utils import timezone
from django.views.generic import TemplateView

from apps.estoque.models.movimento import MovimentoEstoque
from apps.estoque.models.produto import Produto


class DashboardView(TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoje = timezone.localdate()

        movimentacoes_hoje = MovimentoEstoque.objects.filter(data_movimento__date=hoje)

        ctx["entradas_hoje"] = movimentacoes_hoje.filter(operacao="entrada").count()
        ctx["saidas_hoje"] = movimentacoes_hoje.filter(operacao="saida").count()
        ctx["total_produtos"] = Produto.objects.filter(ativo=True).count()
        ctx["produtos_criticos"] = Produto.objects.filter(
            ativo=True,
            estoque_atual__lte=F("estoque_minimo"),
        ).order_by("nome")

        return ctx
