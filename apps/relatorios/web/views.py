from django.views.generic import ListView, TemplateView

from apps.estoque.models.movimento import MovimentoEstoque


class RelatoriosListView(TemplateView):
    template_name = "relatorios/relatorios_list.html"


class MovimentacaoLogView(ListView):
    model = MovimentoEstoque
    template_name = "relatorios/movimentacao_log.html"
    context_object_name = "movimentacoes"
    ordering = ["-data_movimento"]
    paginate_by = 50