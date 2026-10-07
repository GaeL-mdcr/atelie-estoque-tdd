"""
Testes da compra: cada item sabe quanto custou e quanto entra no estoque,
e a compra junta os itens até ser confirmada.
"""

from decimal import Decimal

from apps.compras.dominio import ItemCompra
from apps.conversoes.dominio import ConversaoUnidade

AZUL = 10  # variante Tecido Oxford Azul
TECIDO = 1
METRO = 1
ROLO = 2


def item_em_metro(qtd, preco):
    """Comprou na mesma unidade em que guarda: metro."""
    return ItemCompra(AZUL, TECIDO, METRO, METRO, qtd, preco)


def item_em_rolo(qtd, preco, conversao):
    """Comprou em rolo, guarda em metro."""
    return ItemCompra(AZUL, TECIDO, ROLO, METRO, qtd, preco, conversao)


def deve_calcular_total_do_item():
    assert item_em_metro("3", "7.50").total() == Decimal("22.50")


def deve_entrar_a_mesma_quantidade_quando_unidades_sao_iguais():
    assert item_em_metro("3", "7.50").qtd_entrada_estoque == Decimal("3.000")


# Exemplo da Referência SQL: 2 rolos a R$ 80, com 1 rolo = 20 m.
def deve_converter_a_entrada_quando_comprou_em_rolo():
    item = item_em_rolo("2", "80", ConversaoUnidade(TECIDO, ROLO, "1", "20"))
    assert item.qtd_entrada_estoque == Decimal("40.000")
    assert item.total() == Decimal("160.00")
