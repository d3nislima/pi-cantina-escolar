from django.urls import path

from .views import MovimentacaoLogView, RelatoriosListView, VendaListView

urlpatterns = [
    path("", RelatoriosListView.as_view(), name="relatorios-list"),
    path("movimentacoes/", MovimentacaoLogView.as_view(), name="movimentacao-log"),
    path("vendas/", VendaListView.as_view(), name="venda-list"),
]