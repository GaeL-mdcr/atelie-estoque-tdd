"""
Números do ateliê: dinheiro, quantidade e fator de conversão.

Tudo é Decimal, nunca float. Um float como 0.1 vira 0.1000000000000000055...
e esse resto aparece no custo médio depois de algumas compras.
"""

from decimal import Decimal


def decimal_de(valor):
    return Decimal(valor)
