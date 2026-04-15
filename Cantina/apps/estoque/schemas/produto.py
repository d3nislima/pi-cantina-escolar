from decimal import Decimal

from pydantic import Field

from apps.core.schemas.base import AuditadoSchema, CantinaSchema


class CategoriaBaseSchema(CantinaSchema):
    nome: str = Field(min_length=2, max_length=50)
    descricao: str | None = Field(default=None, max_length=255)
    categoria_pai_id: int | None = None


class CategoriaReadSchema(AuditadoSchema, CategoriaBaseSchema):
    id: int


class ProdutoBaseSchema(CantinaSchema):
    nome: str = Field(min_length=2, max_length=120)
    codigo_barras: str | None = Field(default=None, max_length=40)
    categoria_id: int
    unidade_medida: str = Field(default="un", max_length=10)
    preco_custo: Decimal = Field(default=Decimal("0"), ge=0)
    preco_venda: Decimal = Field(default=Decimal("0"), ge=0)
    estoque_minimo: Decimal = Field(default=Decimal("0"), ge=0)
    ativo: bool = True


class ProdutoCreateSchema(ProdutoBaseSchema):
    pass


class ProdutoReadSchema(AuditadoSchema, ProdutoBaseSchema):
    id: int
    estoque_atual: Decimal
