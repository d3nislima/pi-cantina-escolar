from decimal import Decimal
from django import template

register = template.Library()


@register.filter
def brl(value):
    if value is None:
        return ""
    try:
        value = Decimal(str(value))
    except Exception:
        return value

    negativo = value < 0
    value = abs(value)

    inteiro = int(value)
    centavos = value - Decimal(inteiro)

    inteiro_fmt = f"{inteiro:,}".replace(",", ".")
    centavos_str = f"{centavos:.2f}"[2:]
    resultado = f"R$ {inteiro_fmt},{centavos_str}"

    return f"-{resultado}" if negativo else resultado


UNIDADE_ABREV = {
    "un": "un.",
    "kg": "kg",
    "lt": "lt",
    "pct": "pct",
}


@register.filter
def qtd_unidade(quantidade, unidade):
    if quantidade is None:
        return ""
    try:
        qty = Decimal(str(quantidade))
    except Exception:
        return str(quantidade)

    qty_r = Decimal(f"{qty:.2f}")
    if qty_r == qty_r.to_integral_value():
        qty_str = str(int(qty_r))
    else:
        centavos = str(qty_r).split(".")[1].rstrip("0")
        qty_str = f"{int(qty_r)},{centavos}"

    abrev = UNIDADE_ABREV.get(unidade, unidade)
    return f"{qty_str} {abrev}"
