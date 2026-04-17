from datetime import datetime, timezone as datetime_timezone
from decimal import Decimal
from enum import StrEnum

from pydantic import Field, model_validator

from apps.core.schemas.base import AuditadoSchema, CantinaSchema

class FormaPagamento(StrEnum):
    DINHEIRO = "dinheiro"
    PIX = "pix"
    CARTAO = "cartao"
    CREDITO_INTERNO = "credito_interno"


class JanelaAtendimento(StrEnum):
    RECREIO_MANHA = "recreio_manha"
    ALMOCO = "almoco"
    RECREIO_TARDE = "recreio_tarde"
    FORA_INTERVALO = "fora_intervalo"
    EVENTO_ESPECIAL = "evento_especial"


class ModoAtendimento(StrEnum):
    RAPIDO = "rapido"
    NORMAL = "normal"
    PEDIDO_ANTECIPADO = "pedido_antecipado"


class ItemVendaSchema(CantinaSchema):
    produto_id: int | None = None
    produto_codigo: str | None = Field(default=None, max_length=40)
    produto_nome: str | None = Field(default=None, max_length=120)
    quantidade: Decimal = Field(default=Decimal("1"), gt=0)
    valor_unitario: Decimal | None = Field(default=None, ge=0)
    desconto: Decimal = Field(default=Decimal("0"), ge=0)
    observacao: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validar_referencia(self):
        if not (self.produto_id or self.produto_codigo or self.produto_nome):
            raise ValueError("Informe produto_id, produto_codigo ou produto_nome.")
        return self

    @model_validator(mode="after")
    def validar_valores(self):
        if self.valor_unitario is not None and self.desconto > self.quantidade * self.valor_unitario:
            raise ValueError("Desconto nao pode superar o total do item.")
        return self


class VendaCreateSchema(CantinaSchema):
    itens: list[ItemVendaSchema]
    forma_pagamento: FormaPagamento
    vendido_em: datetime = Field(default_factory=lambda: datetime.now(datetime_timezone.utc), alias="data_venda")
    registrado_em: datetime = Field(default_factory=lambda: datetime.now(datetime_timezone.utc))
    janela_atendimento: JanelaAtendimento = JanelaAtendimento.FORA_INTERVALO
    modo_atendimento: ModoAtendimento = ModoAtendimento.RAPIDO
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
    vendido_em: datetime
    registrado_em: datetime
    janela_atendimento: JanelaAtendimento
    modo_atendimento: ModoAtendimento
    valor_bruto: Decimal
    valor_descontos: Decimal = Field(default=Decimal("0"), ge=0)
    valor_total: Decimal
    valor_recebido: Decimal | None = None
    troco: Decimal | None = None
    observacao: str | None = None
