from django.views.generic import TemplateView


class ProdutoListView(TemplateView):
    template_name = "estoque/produto_list.html"


class MovimentacaoListView(TemplateView):
    template_name = "estoque/movimentacao_list.html"