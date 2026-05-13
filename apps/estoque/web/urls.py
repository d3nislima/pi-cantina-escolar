from django.urls import path

from .views import (
    CategoriaCreateView,
    CategoriaListView,
    CategoriaToggleAtivoView,
    CategoriaUpdateView,
    EstoqueListView,
    MovimentacaoCreateView,
    ProdutoCreateView,
    ProdutoToggleView,
    ProdutoUpdateView,
)

urlpatterns = [
    path("", EstoqueListView.as_view(), name="produto-list"),
    path("produtos/novo/", ProdutoCreateView.as_view(), name="produto-create"),
    path("produtos/<int:pk>/toggle/<str:campo>/", ProdutoToggleView.as_view(), name="produto-toggle"),
    path("produtos/<int:pk>/editar/", ProdutoUpdateView.as_view(), name="produto-update"),
    path("movimentacoes/nova/", MovimentacaoCreateView.as_view(), name="movimentacao-create"),
    path("categorias/", CategoriaListView.as_view(), name="categoria-list"),
    path("categorias/nova/", CategoriaCreateView.as_view(), name="categoria-create"),
    path("categorias/<int:pk>/editar/", CategoriaUpdateView.as_view(), name="categoria-update"),
    path("categorias/<int:pk>/toggle-ativo/", CategoriaToggleAtivoView.as_view(), name="categoria-toggle-ativo"),
]
