from decimal import Decimal
from django.test import TestCase
from apps.core.templatetags.cantina_filters import qtd_unidade


class QtdUnidadeFilterTest(TestCase):
    def test_inteiro_un(self):
        self.assertEqual(qtd_unidade(Decimal("3"), "un"), "3 un.")

    def test_decimal_kg(self):
        self.assertEqual(qtd_unidade(Decimal("0.5"), "kg"), "0,5 kg")

    def test_inteiro_pct(self):
        self.assertEqual(qtd_unidade(Decimal("12"), "pct"), "12 pct")

    def test_zero(self):
        self.assertEqual(qtd_unidade(Decimal("0"), "un"), "0 un.")

    def test_unidade_desconhecida(self):
        self.assertEqual(qtd_unidade(Decimal("2"), "cx"), "2 cx")

    def test_none_retorna_vazio(self):
        self.assertEqual(qtd_unidade(None, "un"), "")
