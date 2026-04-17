from django.views.generic import TemplateView


class VendaListView(TemplateView):
    template_name = "vendas/venda_list.html"