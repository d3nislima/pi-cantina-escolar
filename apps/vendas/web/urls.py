from django.urls import path

from .views import (
    AdicionarItemView,
    FinalizarVendaView,
    JanelaCreateView,
    JanelaToggleAtivoView,
    JanelaUpdateView,
    NovaVendaView,
    RemoverItemView,
    VendaListView,
)

urlpatterns = [
    path("", VendaListView.as_view(), name="venda-list"),
    path("nova/", NovaVendaView.as_view(), name="venda-create"),
    path("adicionar-item/", AdicionarItemView.as_view(), name="venda-adicionar-item"),
    path("remover-item/", RemoverItemView.as_view(), name="venda-remover-item"),
    path("finalizar/", FinalizarVendaView.as_view(), name="venda-finalizar"),
    path("janelas/nova/", JanelaCreateView.as_view(), name="janela-create"),
    path("janelas/<int:pk>/editar/", JanelaUpdateView.as_view(), name="janela-update"),
    path("janelas/<int:pk>/toggle-ativo/", JanelaToggleAtivoView.as_view(), name="janela-toggle-ativo"),
]
