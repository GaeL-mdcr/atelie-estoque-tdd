"""
Testes dos números do ateliê.

Dinheiro e quantidade nunca passam por float: tudo vira Decimal logo na entrada,
para não perder centavo nem milímetro no caminho.
"""

from decimal import Decimal

import pytest

from apps.comum.erros import ValorInvalidoError
from apps.comum.numeros import decimal_de


def deve_converter_texto_e_inteiro_para_decimal():
    assert decimal_de("1.5") == Decimal("1.5")
    assert decimal_de(2) == Decimal("2")
    assert decimal_de(Decimal("3.25")) == Decimal("3.25")


# 0.1 chegando do JSON é o caso clássico: tem que ser recusado, não arredondado.
# True também, porque para o Python ele é o número 1.
@pytest.mark.parametrize("valor", [0.1, 2.0, True])
def nao_deve_aceitar_float_nem_bool(valor):
    with pytest.raises(ValorInvalidoError):
        decimal_de(valor)
