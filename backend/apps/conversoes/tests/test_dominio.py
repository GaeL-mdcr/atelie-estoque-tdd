"""
Testes da conversão de unidades: como transformar o que foi comprado (rolo,
pacote) na unidade em que o material fica no estoque (metro, unidade).
"""

from decimal import Decimal

import pytest

from apps.comum.erros import QuantidadeInvalidaError
from apps.conversoes.dominio import ConversaoUnidade

TECIDO = 1
METRO = 1
ROLO = 2


def deve_calcular_fator_quando_um_rolo_vale_cinquenta_metros():
    assert ConversaoUnidade(TECIDO, ROLO, "1", "50").fator() == Decimal("50.000000")


def deve_calcular_fator_quando_tres_unidades_valem_uma():
    assert ConversaoUnidade(TECIDO, ROLO, "3", "1").fator() == Decimal("0.333333")


def deve_converter_quantidade_comprada_para_unidade_de_estoque():
    rolo = ConversaoUnidade(TECIDO, ROLO, "1", "50")
    assert rolo.converter("2") == Decimal("100.000")
    assert rolo.converter("1.5") == Decimal("75.000")
    # 3 × 0,333333 = 0,999999, que arredondado para 3 casas dá 1,000.
    assert ConversaoUnidade(TECIDO, ROLO, "3", "1").converter("3") == Decimal("1.000")


def deve_atender_somente_o_mesmo_material_e_a_mesma_unidade():
    rolo = ConversaoUnidade(TECIDO, ROLO, "1", "50")
    assert rolo.atende(TECIDO, ROLO) is True
    assert rolo.atende(TECIDO, 3) is False
    assert rolo.atende(9, ROLO) is False


# Fator com zero embaixo não existe, e "0 rolo = 50 m" não faz sentido.
@pytest.mark.parametrize("compra,estoque", [("0", "50"), ("1", "0"), ("-1", "50")])
def nao_deve_aceitar_equivalencia_zero_ou_negativa(compra, estoque):
    with pytest.raises(QuantidadeInvalidaError):
        ConversaoUnidade(TECIDO, ROLO, compra, estoque)


@pytest.mark.parametrize("qtd", ["0", "-2"])
def nao_deve_converter_quantidade_zero_ou_negativa(qtd):
    with pytest.raises(QuantidadeInvalidaError):
        ConversaoUnidade(TECIDO, ROLO, "1", "50").converter(qtd)
