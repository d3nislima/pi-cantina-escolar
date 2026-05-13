from django.urls import path

from .views import ConfiguracoesView, DashboardView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("configuracoes/", ConfiguracoesView.as_view(), name="configuracoes"),
]
