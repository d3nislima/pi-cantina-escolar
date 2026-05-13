from django.urls import path

from .views import MovimentacaoLogView, RelatoriosListView

urlpatterns = [
    path("", RelatoriosListView.as_view(), name="relatorios-list"),
    path("movimentacoes/", MovimentacaoLogView.as_view(), name="movimentacao-log"),
]