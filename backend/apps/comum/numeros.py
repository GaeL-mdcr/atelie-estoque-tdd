"""
Números do ateliê: dinheiro, quantidade e fator de conversão.

Tudo é Decimal, nunca float. Um float como 0.1 vira 0.1000000000000000055...
e esse resto aparece no custo médio depois de algumas compras.
"""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from apps.comum.erros import ValorInvalidoError

CASAS_QUANTIDADE = Decimal("0.001")
CASAS_DINHEIRO = Decimal("0.01")
CASAS_FATOR = Decimal("0.000001")

NAO_E_NUMERO = "Esse valor não é um número que o ateliê consiga usar."


def decimal_de(valor):
    # bool e float são recusados antes de tudo: True é o número 1 para o Python
    # e 0.1 já chega com sujeira de arredondamento.
    if isinstance(valor, (bool, float)):
        raise ValorInvalidoError(NAO_E_NUMERO)
    try:
        numero = Decimal(valor)
    except (InvalidOperation, TypeError):
        raise ValorInvalidoError(NAO_E_NUMERO) from None
    if not numero.is_finite():
        raise ValorInvalidoError(NAO_E_NUMERO)
    return numero



def _arredondar(valor, casas):
    return decimal_de(valor).quantize(casas, rounding=ROUND_HALF_UP)


def quantidade(valor):
    return _arredondar(valor, CASAS_QUANTIDADE)


def dinheiro(valor):
    return _arredondar(valor, CASAS_DINHEIRO)


def fator(valor):
    return _arredondar(valor, CASAS_FATOR)
