from django.db import models

from apps.core.models.base import AuditadoModel
from apps.estoque.models.produto import Produto


class MovimentoEstoque(AuditadoModel):
    OPERACAO_CHOICES = [
        ("entrada", "Entrada"),
        ("saida", "Saida"),
        ("ajuste", "Ajuste"),
    ]

    ORIGEM_CHOICES = [
        ("compra", "Compra"),
        ("venda", "Venda"),
        ("perda", "Perda"),
        ("inventario", "Inventario"),
        ("doacao", "Doacao"),
        ("ajuste_manual", "Ajuste Manual"),
    ]

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name="movimentacoes",
        verbose_name="Produto",
    )
    operacao = models.CharField(
        max_length=10,
        choices=OPERACAO_CHOICES,
        verbose_name="Operacao",
    )
    origem = models.CharField(
        max_length=20,
        choices=ORIGEM_CHOICES,
        verbose_name="Origem",
    )
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantidade")
    valor_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Unitario",
    )
    saldo_antes = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Saldo Antes",
    )
    saldo_depois = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Saldo Depois",
    )
    documento_referencia = models.CharField(
        max_length=60,
        blank=True,
        null=True,
        verbose_name="Documento de Referencia",
    )
    observacao = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Observacao",
    )
    data_movimento = models.DateTimeField(verbose_name="Data do Movimento")

    class Meta:
        verbose_name = "Movimento de Estoque"
        verbose_name_plural = "Movimentos de Estoque"
        ordering = ["-data_movimento"]

    def __str__(self):
        return f"{self.operacao.capitalize()} - {self.produto.nome} ({self.quantidade})"
