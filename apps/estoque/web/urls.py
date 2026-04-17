from django.urls import path

from .views import MovimentacaoListView, ProdutoListView

urlpatterns = [
    path("produtos/", ProdutoListView.as_view(), name="produto-list"),
    path("movimentacoes/", MovimentacaoListView.as_view(), name="movimentacao-list"),
]