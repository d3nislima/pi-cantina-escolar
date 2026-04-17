from django.urls import path

from .views import (
    MovimentacaoCreateView,
    MovimentacaoListView,
    ProdutoCreateView,
    ProdutoListView,
    ProdutoUpdateView,
)

urlpatterns = [
    path("produtos/", ProdutoListView.as_view(), name="produto-list"),
    path("produtos/novo/", ProdutoCreateView.as_view(), name="produto-create"),
    path("produtos/<int:pk>/editar/", ProdutoUpdateView.as_view(), name="produto-update"),
    path("movimentacoes/", MovimentacaoListView.as_view(), name="movimentacao-list"),
    path("movimentacoes/nova/", MovimentacaoCreateView.as_view(), name="movimentacao-create"),
]