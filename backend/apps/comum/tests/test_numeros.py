"""
Testes dos números do ateliê.

Dinheiro e quantidade nunca passam por float: tudo vira Decimal logo na entrada,
para não perder centavo nem milímetro no caminho.
"""

from decimal import Decimal

import pytest

from apps.comum.erros import (
    ErroDeNegocio,
    QuantidadeInvalidaError,
    ValorInvalidoError,
    ValorObrigatorioError,
)
from apps.comum.numeros import (
    decimal_de,
    dinheiro,
    exigir_nao_negativo,
    exigir_positivo,
    fator,
    quantidade,
    texto_obrigatorio,
)


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


# NaN e Infinity são Decimal válidos para o Python, mas não existe "infinito metros" de tecido.
@pytest.mark.parametrize("valor", ["abc", "", None, "NaN", "Infinity"])
def nao_deve_aceitar_valor_que_nao_e_numero(valor):
    with pytest.raises(ValorInvalidoError):
        decimal_de(valor)


# Dinheiro com 2 casas, quantidade com 3 e fator com 6, sempre "meio para cima".
def deve_arredondar_meio_para_cima_em_cada_escala():
    assert dinheiro("2.345") == Decimal("2.35")
    assert dinheiro("2") == Decimal("2.00")
    assert quantidade("1.2345") == Decimal("1.235")
    assert fator("0.3333335") == Decimal("0.333334")


# A mensagem cita o campo, para a tela dizer exatamente o que está errado.
def deve_validar_positivo_nao_negativo_e_texto():
    assert exigir_positivo("0.001", "quantidade") == Decimal("0.001")
    assert exigir_nao_negativo("0", "preço") == Decimal("0")
    assert texto_obrigatorio("  Azul ", "nome") == "Azul"
    with pytest.raises(QuantidadeInvalidaError, match="quantidade"):
        exigir_positivo("0", "quantidade")
    with pytest.raises(ValorInvalidoError, match="preço"):
        exigir_nao_negativo("-0.01", "preço")
    with pytest.raises(ValorObrigatorioError, match="nome"):
        texto_obrigatorio("   ", "nome")
    assert issubclass(QuantidadeInvalidaError, ErroDeNegocio)
