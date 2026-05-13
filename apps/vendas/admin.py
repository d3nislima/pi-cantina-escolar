from django.contrib import admin

from apps.vendas.models.venda import ItemVenda, JanelaAtendimento, Venda

admin.site.register(JanelaAtendimento)
admin.site.register(Venda)
admin.site.register(ItemVenda)
