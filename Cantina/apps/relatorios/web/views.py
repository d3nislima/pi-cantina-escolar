from django.views.generic import TemplateView


class RelatoriosListView(TemplateView):
    template_name = "relatorios/relatorios_list.html"