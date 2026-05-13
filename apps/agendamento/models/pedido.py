from django.db import models

from apps.core.models.base import AuditadoModel
from apps.estoque.models.produto import Produto
from apps.vendas.models.venda import JanelaAtendimento


class PedidoAntecipado(AuditadoModel):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("retirado", "Retirado"),
        ("expirado", "Expirado"),
    ]

    nome_aluno = models.CharField(max_length=100, verbose_name="Nome do Aluno")
    turma = models.CharField(max_length=20, verbose_name="Turma")
    janela_atendimento = models.ForeignKey(
        JanelaAtendimento,
        on_delete=models.PROTECT,
        related_name="pedidos",
        verbose_name="Período de Retirada",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pendente",
        verbose_name="Status",
    )
    observacao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Observação")

    class Meta:
        verbose_name = "Pedido Antecipado"
        verbose_name_plural = "Pedidos Antecipados"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.nome_aluno} ({self.turma}) — {self.janela_atendimento.nome}"


class ItemPedido(AuditadoModel):
    pedido = models.ForeignKey(
        PedidoAntecipado,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="Pedido",
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name="pedidos",
        verbose_name="Produto",
    )
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantidade")
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Unitário")

    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"

    def __str__(self):
        return f"{self.produto.nome} ({self.quantidade})"

    @property
    def valor_total(self):
        return self.quantidade * self.valor_unitario
