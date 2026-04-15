from django.db import models

from apps.core.models.base import AuditadoModel
from apps.estoque.models.produto import Produto


class Venda(AuditadoModel):
    PAGAMENTO_CHOICES = [
        ("dinheiro", "Dinheiro"),
        ("pix", "PIX"),
        ("cartao", "Cartao"),
        ("credito_interno", "Credito Interno"),
    ]

    JANELA_CHOICES = [
        ("recreio_manha", "Recreio Manha"),
        ("almoco", "Almoco"),
        ("recreio_tarde", "Recreio Tarde"),
        ("fora_intervalo", "Fora de Intervalo"),
        ("evento_especial", "Evento Especial"),
    ]

    MODO_CHOICES = [
        ("rapido", "Rapido"),
        ("normal", "Normal"),
        ("pedido_antecipado", "Pedido Antecipado"),
    ]

    forma_pagamento = models.CharField(
        max_length=20,
        choices=PAGAMENTO_CHOICES,
        verbose_name="Forma de Pagamento",
    )
    janela_atendimento = models.CharField(
        max_length=20,
        choices=JANELA_CHOICES,
        default="fora_intervalo",
        verbose_name="Janela de Atendimento",
    )
    modo_atendimento = models.CharField(
        max_length=20,
        choices=MODO_CHOICES,
        default="rapido",
        verbose_name="Modo de Atendimento",
    )
    valor_bruto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor Bruto")
    valor_descontos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor Descontos",
    )
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor Total")
    valor_recebido = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor Recebido",
    )
    troco = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Troco",
    )
    vendido_em = models.DateTimeField(verbose_name="Vendido em")
    registrado_em = models.DateTimeField(auto_now_add=True, verbose_name="Registrado em")
    observacao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Observacao")

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"
        ordering = ["-vendido_em"]

    def __str__(self):
        return f"Venda {self.id} - {self.vendido_em.strftime('%d/%m/%Y %H:%M')}"


class ItemVenda(AuditadoModel):
    venda = models.ForeignKey(
        Venda,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="Venda",
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name="vendas",
        verbose_name="Produto",
    )
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name="Quantidade")
    valor_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Unitario",
    )
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Desconto")
    valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Total",
    )
    observacao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Observacao")

    class Meta:
        verbose_name = "Item de Venda"
        verbose_name_plural = "Itens de Venda"

    def __str__(self):
        return f"{self.produto.nome} ({self.quantidade})"
