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


# Exemplo da Referência SQL: 10 m a R$ 7,00 + 40 m por R$ 160 → (70 + 160) ÷ 50 = R$ 4,60.
def deve_recalcular_media_ponderada_quando_entra_compra():
    estoque = EstoqueVariante("10", "7")
    estoque.registrar_entrada("40", "160")
    assert estoque.saldo == Decimal("50.000")
    assert estoque.custo_medio == Decimal("4.60")
