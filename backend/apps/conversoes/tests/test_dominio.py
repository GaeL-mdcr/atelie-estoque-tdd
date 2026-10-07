"""
Testes da conversão de unidades: como transformar o que foi comprado (rolo,
pacote) na unidade em que o material fica no estoque (metro, unidade).
"""

from decimal import Decimal

from apps.conversoes.dominio import ConversaoUnidade

TECIDO = 1
METRO = 1
ROLO = 2


def deve_calcular_fator_quando_um_rolo_vale_cinquenta_metros():
    assert ConversaoUnidade(TECIDO, ROLO, "1", "50").fator() == Decimal("50.000000")


def deve_calcular_fator_quando_tres_unidades_valem_uma():
    assert ConversaoUnidade(TECIDO, ROLO, "3", "1").fator() == Decimal("0.333333")
