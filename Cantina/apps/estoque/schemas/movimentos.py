from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import Field

from apps.core.schemas.base import AuditadoSchema, CantinaSchema


class OperacaoEstoque(StrEnum):
    ENTRADA = "entrada"
    SAIDA = "saida"
    AJUSTE = "ajuste"


class OrigemMovimentoEstoque(StrEnum):
    COMPRA = "compra"
    VENDA = "venda"
    PERDA = "perda"
    INVENTARIO = "inventario"
    DOACAO = "doacao"
    AJUSTE_MANUAL = "ajuste_manual"


class MovimentoEstoqueBaseSchema(CantinaSchema):
    produto_nome: str = Field(min_length=2, max_length=120)
    operacao: OperacaoEstoque
    origem: OrigemMovimentoEstoque
    quantidade: Decimal = Field(gt=0)
    valor_unitario: Decimal = Field(ge=0)
    documento_referencia: str | None = Field(default=None, max_length=60)
    observacao: str | None = Field(default=None, max_length=255)
    data_movimento: datetime


class MovimentoEstoqueCreateSchema(MovimentoEstoqueBaseSchema):
    fornecedor_nome: str | None = Field(default=None, max_length=120)
    data_compra: date | None = None


class MovimentoEstoqueReadSchema(AuditadoSchema, MovimentoEstoqueBaseSchema):
    id: int | str | None = None
    saldo_antes: Decimal | None = None
    saldo_depois: Decimal | None = None
