"""
Testes da compra: cada item sabe quanto custou e quanto entra no estoque,
e a compra junta os itens até ser confirmada.
"""

from decimal import Decimal

from apps.compras.dominio import ItemCompra

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
