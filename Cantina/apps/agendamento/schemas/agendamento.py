from datetime import date, datetime
from decimal import Decimal

from pydantic import EmailStr, Field

from apps.core.schemas.base import AuditadoSchema, CantinaSchema


class FornecedorBaseSchema(CantinaSchema):
    nome: str = Field(min_length=2, max_length=100)
    cnpj: str | None = Field(default=None, min_length=14, max_length=14)
    contato: str | None = Field(default=None, max_length=200)
    email: EmailStr | None = None
    telefone: str | None = Field(default=None, max_length=20)
    ativo: bool = True


class FornecedorReadSchema(AuditadoSchema, FornecedorBaseSchema):
    id: int


class ContaAPagarBaseSchema(CantinaSchema):
    descricao: str = Field(min_length=2, max_length=255)
    fornecedor_id: int | None = None
    valor: Decimal = Field(gt=0)
    data_vencimento: date
    status: str = Field(default="pendente")
    observacao: str | None = Field(default=None)


class ContaAPagarReadSchema(AuditadoSchema, ContaAPagarBaseSchema):
    id: int
    data_pagamento: date | None = None


class EntregaAgendadaBaseSchema(CantinaSchema):
    fornecedor_id: int
    data_prevista: datetime
    status: str = Field(default="agendado")
    observacao: str | None = Field(default=None)


class EntregaAgendadaReadSchema(AuditadoSchema, EntregaAgendadaBaseSchema):
    id: int
    data_recebimento: datetime | None = None
