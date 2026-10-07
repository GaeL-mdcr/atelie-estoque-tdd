"""
Conversão entre a unidade de compra e a unidade de estoque de um material.

Exemplo do ateliê: o tecido é comprado em rolo e guardado em metro,
e 1 rolo = 50 m. O fator é estoque ÷ compra.
"""

from apps.comum.numeros import decimal_de, exigir_positivo, fator, quantidade


class ConversaoUnidade:
    def __init__(self, material_id, unidade_compra_id, qtd_equivalente_compra, qtd_equivalente_estoque):
        self.material_id = material_id
        self.unidade_compra_id = unidade_compra_id
        self.qtd_equivalente_compra = exigir_positivo(qtd_equivalente_compra, "quantidade na unidade de compra")
        self.qtd_equivalente_estoque = exigir_positivo(qtd_equivalente_estoque, "quantidade na unidade de estoque")

    def fator(self):
        return fator(self.qtd_equivalente_estoque / self.qtd_equivalente_compra)

    def converter(self, qtd_compra):
        return quantidade(decimal_de(qtd_compra) * self.fator())

    def atende(self, material_id, unidade_compra_id):
        return self.material_id == material_id and self.unidade_compra_id == unidade_compra_id
