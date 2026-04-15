from django.db import models

from apps.core.models.base import AuditadoModel


class Fornecedor(AuditadoModel):
    nome = models.CharField(max_length=100, verbose_name="Nome")
    cnpj = models.CharField(max_length=14, unique=True, blank=True, null=True, verbose_name="CNPJ")
    contato = models.CharField(max_length=200, blank=True, null=True, verbose_name="Contato")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class ContaAPagar(AuditadoModel):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("pago", "Pago"),
        ("cancelado", "Cancelado"),
    ]

    descricao = models.CharField(max_length=255, verbose_name="Descricao")
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contas",
        verbose_name="Fornecedor",
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    data_pagamento = models.DateField(null=True, blank=True, verbose_name="Data de Pagamento")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pendente",
        verbose_name="Status",
    )
    observacao = models.TextField(blank=True, null=True, verbose_name="Observacao")

    class Meta:
        verbose_name = "Conta a Pagar"
        verbose_name_plural = "Contas a Pagar"
        ordering = ["data_vencimento"]

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} ({self.status})"


class EntregaAgendada(AuditadoModel):
    STATUS_CHOICES = [
        ("agendado", "Agendado"),
        ("recebido", "Recebido"),
        ("atrasado", "Atrasado"),
        ("cancelado", "Cancelado"),
    ]

    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.CASCADE,
        related_name="entregas",
        verbose_name="Fornecedor",
    )
    data_prevista = models.DateTimeField(verbose_name="Data Prevista")
    data_recebimento = models.DateTimeField(null=True, blank=True, verbose_name="Data de Recebimento")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="agendado",
        verbose_name="Status",
    )
    observacao = models.TextField(blank=True, null=True, verbose_name="Observacao")

    class Meta:
        verbose_name = "Entrega Agendada"
        verbose_name_plural = "Entregas Agendadas"
        ordering = ["data_prevista"]

    def __str__(self):
        return f"Entrega {self.fornecedor.nome} - {self.data_prevista.strftime('%d/%m/%Y')}"
