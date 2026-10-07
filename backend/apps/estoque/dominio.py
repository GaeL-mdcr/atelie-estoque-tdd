"""
Estoque de uma variante (material + cor): saldo e custo médio ponderado.

Cada cor tem o seu: mexer no Azul não muda o Branco do mesmo tecido.
"""

from apps.comum.numeros import dinheiro, quantidade


class EstoqueVariante:
    def __init__(self, qtd_inicial="0", vl_unitario_inicial="0", qtd_estoque_minimo="0"):
        self._saldo = quantidade(qtd_inicial)
        self._custo_medio = dinheiro(vl_unitario_inicial)

    @property
    def saldo(self):
        return self._saldo

    @property
    def custo_medio(self):
        return self._custo_medio
