from decimal import Decimal
from enum import StrEnum

from pydantic import Field

from apps.core.schemas.base import PeriodoSchema


class TipoRelatorio(StrEnum):
    BALANCO = "balanco"
    FISCAL = "fiscal"
    CAIXA = "caixa"
    ESTOQUE = "estoque"


class ResumoFiscalSchema(PeriodoSchema):
    tipo_relatorio: TipoRelatorio = TipoRelatorio.FISCAL
    receita_bruta: Decimal = Field(ge=0)
    descontos: Decimal = Field(default=Decimal("0"), ge=0)
    custo_mercadorias: Decimal = Field(default=Decimal("0"), ge=0)
    despesas_operacionais: Decimal = Field(default=Decimal("0"), ge=0)
    tributos_estimados: Decimal = Field(default=Decimal("0"), ge=0)
    lucro_bruto: Decimal
    lucro_liquido: Decimal
    observacao: str | None = Field(default=None, max_length=255)


class BalancoOperacionalSchema(PeriodoSchema):
    tipo_relatorio: TipoRelatorio = TipoRelatorio.BALANCO
    entradas_caixa: Decimal = Field(ge=0)
    saidas_caixa: Decimal = Field(ge=0)
    saldo_inicial: Decimal = Field(default=Decimal("0"), ge=0)
    saldo_final: Decimal
    divergencia: Decimal
