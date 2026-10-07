"""
Testes dos números do ateliê.

Dinheiro e quantidade nunca passam por float: tudo vira Decimal logo na entrada,
para não perder centavo nem milímetro no caminho.
"""

from decimal import Decimal

from apps.comum.numeros import decimal_de


def deve_converter_texto_e_inteiro_para_decimal():
    assert decimal_de("1.5") == Decimal("1.5")
    assert decimal_de(2) == Decimal("2")
    assert decimal_de(Decimal("3.25")) == Decimal("3.25")
