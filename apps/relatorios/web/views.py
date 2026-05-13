from django.views.generic import ListView, TemplateView

from apps.estoque.models.movimento import MovimentoEstoque
from apps.vendas.models.venda import Venda


class RelatoriosListView(TemplateView):
    template_name = "relatorios/relatorios_list.html"


class MovimentacaoLogView(ListView):
    model = MovimentoEstoque
    template_name = "relatorios/movimentacao_log.html"
    context_object_name = "movimentacoes"
    ordering = ["-data_movimento"]
    paginate_by = 50


class VendaListView(ListView):
    model = Venda
    template_name = "vendas/venda_list.html"
    context_object_name = "vendas"
    ordering = ["-vendido_em"]
    paginate_by = 50