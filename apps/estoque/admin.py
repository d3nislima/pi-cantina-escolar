from django.contrib import admin

from apps.estoque.models.produto import Categoria, Produto
from apps.estoque.models.movimento import MovimentoEstoque

admin.site.register(Categoria)
admin.site.register(Produto)
admin.site.register(MovimentoEstoque)
