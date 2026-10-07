"""
Números do ateliê: dinheiro, quantidade e fator de conversão.

Tudo é Decimal, nunca float. Um float como 0.1 vira 0.1000000000000000055...
e esse resto aparece no custo médio depois de algumas compras.
"""

from decimal import Decimal

from apps.comum.erros import ValorInvalidoError


def decimal_de(valor):
    # bool vem antes de int de propósito: True também é int para o Python.
    if isinstance(valor, (bool, float)):
        raise ValorInvalidoError("Informe o valor como texto ou número inteiro, não com vírgula flutuante.")
    return Decimal(valor)
