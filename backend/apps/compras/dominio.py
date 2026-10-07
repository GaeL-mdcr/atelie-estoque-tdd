"""
Compra de materiais: os itens e a compra que junta todos eles.
"""

from apps.comum.numeros import dinheiro, quantidade


class ItemCompra:
    def __init__(self, variante_id, material_id, unidade_compra_id, unidade_estoque_id,
                 qtd_compra, vl_unitario_compra, conversao=None):
        self.variante_id = variante_id
        self.qtd_compra = quantidade(qtd_compra)
        self.vl_unitario_compra = dinheiro(vl_unitario_compra)
        if unidade_compra_id == unidade_estoque_id:
            self.qtd_entrada_estoque = self.qtd_compra
        else:
            self.qtd_entrada_estoque = conversao.converter(self.qtd_compra)

    def total(self):
        return dinheiro(self.qtd_compra * self.vl_unitario_compra)

    def custo_unitario_entrada(self):
        return dinheiro(self.total() / self.qtd_entrada_estoque)
