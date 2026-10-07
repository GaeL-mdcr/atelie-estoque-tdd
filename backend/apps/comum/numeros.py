"""
Números do ateliê: dinheiro, quantidade e fator de conversão.

Tudo é Decimal, nunca float. Um float como 0.1 vira 0.1000000000000000055...
e esse resto aparece no custo médio depois de algumas compras.
"""

from decimal import Decimal, InvalidOperation

from apps.comum.erros import ValorInvalidoError


def decimal_de(valor):
    # bool vem antes de int de propósito: True também é int para o Python.
    if isinstance(valor, (bool, float)):
        raise ValorInvalidoError("Esse valor não é um número que o ateliê consiga usar.")
    try:
        numero = Decimal(valor)
    except (InvalidOperation, TypeError):
        raise ValorInvalidoError("Esse valor não é um número que o ateliê consiga usar.") from None
    if not numero.is_finite():
        raise ValorInvalidoError("Esse valor não é um número que o ateliê consiga usar.")
    return numero
