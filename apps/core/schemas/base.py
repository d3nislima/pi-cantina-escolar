from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CantinaSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class AuditadoSchema(CantinaSchema):
    criado_em: datetime | None = None
    atualizado_em: datetime | None = None


class PeriodoSchema(CantinaSchema):
    data_inicio: date
    data_fim: date


class DinheiroSchema(CantinaSchema):
    valor: Decimal = Field(ge=0)
