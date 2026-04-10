from django.urls import path

from .views import VendaListView

urlpatterns = [
    path("", VendaListView.as_view(), name="venda-list"),
]