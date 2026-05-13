from django.urls import path

from .views import AgendarPedidoView, AgendamentoListView, CancelarPedidoView, RetiradaPedidoView

urlpatterns = [
    path("", AgendamentoListView.as_view(), name="agendamento-list"),
    path("novo/", AgendarPedidoView.as_view(), name="agendamento-novo"),
    path("<int:pk>/retirada/", RetiradaPedidoView.as_view(), name="agendamento-retirada"),
    path("<int:pk>/cancelar/", CancelarPedidoView.as_view(), name="agendamento-cancelar"),
]
