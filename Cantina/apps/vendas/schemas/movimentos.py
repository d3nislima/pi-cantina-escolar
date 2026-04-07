from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import Field, model_validator

from apps.core.schemas.base import AuditadoSchema, CantinaSchema

# fml sou fã de pydantic fazer oq

class FormaPagamento(StrEnum):
    DINHEIRO = "dinheiro"
    PIX = "pix"
    CARTAO = "cartao"
    CREDITO_INTERNO = "credito_interno"


class ItemVendaSchema(CantinaSchema):
    produto_nome: str = Field(min_length=2, max_length=120)
    quantidade: Decimal = Field(gt=0)
    valor_unitario: Decimal = Field(ge=0)
    desconto: Decimal = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validar_valores(self):
        if self.desconto > self.quantidade * self.valor_unitario:
            raise ValueError("Desconto nao pode superar o total do item.")
        return self


class VendaCreateSchema(CantinaSchema):
    itens: list[ItemVendaSchema]
    forma_pagamento: FormaPagamento
    data_venda: datetime
    observacao: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validar_itens(self):
        if not self.itens:
            raise ValueError("Venda deve ter ao menos um item.")
        return self


class VendaReadSchema(AuditadoSchema):
    id: int | str | None = None
    itens: list[ItemVendaSchema]
    forma_pagamento: FormaPagamento
    data_venda: datetime
    valor_bruto: Decimal
    valor_descontos: Decimal = Field(default=0, ge=0)
    valor_total: Decimal
    valor_recebido: Decimal | None = None
    troco: Decimal | None = None
    observacao: str | None = None
