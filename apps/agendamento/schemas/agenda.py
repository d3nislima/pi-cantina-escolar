from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import Field

from apps.core.schemas.base import AuditadoSchema, CantinaSchema


class TipoCompromisso(StrEnum):
    FORNECEDOR = "fornecedor"
    CONTA_A_PAGAR = "conta_a_pagar"
    ENTREGA = "entrega"
    COMPRA = "compra"


class FornecedorSchema(CantinaSchema):
    nome: str = Field(min_length=2, max_length=120)
    documento: str | None = Field(default=None, max_length=20)
    contato: str | None = Field(default=None, max_length=120)
    observacao: str | None = Field(default=None, max_length=255)


class ContaPagarSchema(CantinaSchema):
    descricao: str = Field(min_length=2, max_length=120)
    fornecedor_nome: str | None = Field(default=None, max_length=120)
    valor: Decimal = Field(gt=0)
    vencimento: date
    pago: bool = False
    data_pagamento: datetime | None = None
    observacao: str | None = Field(default=None, max_length=255)


class EntregaAgendadaSchema(CantinaSchema):
    fornecedor_nome: str = Field(min_length=2, max_length=120)
    compromisso_em: datetime
    itens_previstos: list[str] = Field(default_factory=list)
    observacao: str | None = Field(default=None, max_length=255)


class RotinaCompraSchema(CantinaSchema):
    titulo: str = Field(min_length=2, max_length=120)
    tipo: TipoCompromisso = TipoCompromisso.COMPRA
    agendada_para: datetime
    valor_estimado: Decimal | None = Field(default=None, ge=0)
    fornecedor_preferencial: str | None = Field(default=None, max_length=120)
    observacao: str | None = Field(default=None, max_length=255)


class CompromissoAgendaReadSchema(AuditadoSchema):
    id: int | str | None = None
    tipo: TipoCompromisso
    titulo: str
    compromisso_em: datetime
    status: str = "aberto"
