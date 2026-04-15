from django.db import models


class AuditadoModel(models.Model):
    """
    Classe base para modelos que precisam de rastreamento de criacao e atualizacao.
    """

    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        abstract = True
