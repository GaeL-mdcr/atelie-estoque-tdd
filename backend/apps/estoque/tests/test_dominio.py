"""
Testes do estoque de uma cor de um material (ex.: Tecido Oxford Azul):
saldo, custo médio ponderado e aviso de estoque mínimo.
"""

from decimal import Decimal

import pytest

from apps.estoque.dominio import EstoqueVariante, SaldoInsuficienteError


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


# Estoque zerado não pode dar divisão por zero: o custo médio vira o custo da compra.
def deve_usar_o_custo_da_compra_quando_estoque_estava_vazio():
    estoque = EstoqueVariante()
    estoque.registrar_entrada("40", "160")
    assert estoque.custo_medio == Decimal("4.00")


# A saída devolve o custo médio do momento, que fica gravado no uso. A média não muda.
def deve_baixar_saldo_e_devolver_custo_vigente_na_saida():
    estoque = EstoqueVariante("50", "4.60")
    assert estoque.registrar_saida("3") == Decimal("4.60")
    assert estoque.saldo == Decimal("47.000")
    assert estoque.custo_medio == Decimal("4.60")


# O erro diz quanto tem, para a tela mostrar "Disponível: 2" e a dona corrigir o número.
def nao_deve_sair_mais_que_o_saldo():
    estoque = EstoqueVariante("2", "5")
    with pytest.raises(SaldoInsuficienteError) as erro:
        estoque.registrar_saida("2.5")
    assert erro.value.disponivel == Decimal("2.000")
    assert estoque.saldo == Decimal("2.000")


# Usar exatamente o que tem pode: o saldo vai a zero, não fica negativo.
def deve_permitir_sair_todo_o_saldo():
    estoque = EstoqueVariante("2", "5")
    estoque.registrar_saida("2")
    assert estoque.saldo == Decimal("0.000")


# O retorno volta com o custo do uso de origem e entra na média ponderada (decisão D05).
def deve_devolver_ao_saldo_e_recalcular_media_no_retorno():
    estoque = EstoqueVariante("47", "4.60")
    estoque.registrar_retorno("0.5", "4.60")
    assert estoque.saldo == Decimal("47.500")
    assert estoque.custo_medio == Decimal("4.60")

    outro = EstoqueVariante("10", "5")
    outro.registrar_retorno("10", "7")
    assert outro.custo_medio == Decimal("6.00")

    vazio = EstoqueVariante()
    vazio.registrar_retorno("1", "4.60")
    assert (vazio.saldo, vazio.custo_medio) == (Decimal("1.000"), Decimal("4.60"))


# Abaixo do mínimo é estritamente menor: com 5 m e mínimo 5 m ainda não precisa avisar.
def deve_avisar_quando_abaixo_do_minimo():
    assert EstoqueVariante("4", "1", "5").abaixo_do_minimo() is True
    assert EstoqueVariante("5", "1", "5").abaixo_do_minimo() is False
