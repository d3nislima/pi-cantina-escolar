from django.urls import path

from .views import RelatoriosListView

urlpatterns = [
    path("", RelatoriosListView.as_view(), name="relatorios-list"),
]