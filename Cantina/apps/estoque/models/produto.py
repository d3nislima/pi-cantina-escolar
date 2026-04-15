from django.db import models

from apps.core.models.base import AuditadoModel


class Categoria(AuditadoModel):
    nome = models.CharField(max_length=50, unique=True, verbose_name="Nome")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descricao")
    categoria_pai = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategorias",
        verbose_name="Categoria Pai",
    )

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["nome"]

    def __str__(self):
        if self.categoria_pai:
            return f"{self.categoria_pai.nome} > {self.nome}"
        return self.nome


class Produto(AuditadoModel):
    UNIDADE_CHOICES = [
        ("un", "Unidade"),
        ("kg", "Quilograma"),
        ("lt", "Litro"),
        ("pct", "Pacote"),
    ]

    nome = models.CharField(max_length=120, verbose_name="Nome")
    codigo_barras = models.CharField(
        max_length=40,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Codigo de Barras",
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="produtos",
        verbose_name="Categoria",
    )
    unidade_medida = models.CharField(
        max_length=10,
        choices=UNIDADE_CHOICES,
        default="un",
        verbose_name="Unidade de Medida",
    )
    preco_custo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Preco de Custo",
    )
    preco_venda = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Preco de Venda",
    )
    estoque_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Estoque Minimo",
    )
    estoque_atual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Estoque Atual",
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["nome"]

    def __str__(self):
        return self.nome
