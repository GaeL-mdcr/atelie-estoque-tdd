"""
Testes do estoque de uma cor de um material (ex.: Tecido Oxford Azul):
saldo, custo médio ponderado e aviso de estoque mínimo.
"""

from decimal import Decimal

import pytest

from apps.estoque.dominio import EstoqueVariante


# Saldo não se edita à mão: ele só muda por compra, uso e retorno.
def deve_comecar_com_saldo_e_custo_iniciais():
    estoque = EstoqueVariante("10", "7", "5")
    assert estoque.saldo == Decimal("10.000")
    assert estoque.custo_medio == Decimal("7.00")
    with pytest.raises(AttributeError):
        estoque.saldo = Decimal("99")
