"""
Compra de materiais: os itens e a compra que junta todos eles.
"""

from apps.comum.erros import ErroDeNegocio
from apps.comum.numeros import dinheiro, exigir_nao_negativo, exigir_positivo, quantidade


class ConversaoAusenteError(ErroDeNegocio):
    """Comprou numa unidade diferente da do estoque e não tem conversão cadastrada."""


class ConversaoIncompativelError(ErroDeNegocio):
    """A conversão informada é de outro material ou de outra unidade de compra."""


class CompraSemItensError(ErroDeNegocio):
    """Tentou confirmar uma compra vazia."""


class CompraConfirmadaError(ErroDeNegocio):
    """Tentou mexer numa compra que já foi confirmada."""


class ItemNaoEncontradoError(ErroDeNegocio):
    """A posição informada não tem item nenhum."""


class ItemCompra:
    def __init__(self, variante_id, material_id, unidade_compra_id, unidade_estoque_id,
                 qtd_compra, vl_unitario_compra, conversao=None):
        self.variante_id = variante_id
        self.qtd_compra = quantidade(exigir_positivo(qtd_compra, "quantidade comprada"))
        self.vl_unitario_compra = dinheiro(exigir_nao_negativo(vl_unitario_compra, "preço unitário"))
        # A entrada é calculada uma vez só e fica guardada: é o histórico da compra (RN09).
        self.qtd_entrada_estoque = self._calcular_entrada(
            material_id, unidade_compra_id, unidade_estoque_id, conversao
        )

    def _calcular_entrada(self, material_id, unidade_compra_id, unidade_estoque_id, conversao):
        if unidade_compra_id == unidade_estoque_id:
            return self.qtd_compra
        if conversao is None:
            raise ConversaoAusenteError(
                "Essa unidade de compra é diferente da do estoque. Cadastre quanto ela vale antes de lançar a compra."
            )
        if not conversao.atende(material_id, unidade_compra_id):
            raise ConversaoIncompativelError("Essa conversão não é deste material ou desta unidade de compra.")
        return conversao.converter(self.qtd_compra)

    def total(self):
        return dinheiro(self.qtd_compra * self.vl_unitario_compra)

    def custo_unitario_entrada(self):
        return dinheiro(self.total() / self.qtd_entrada_estoque)


class Compra:
    def __init__(self, fornecedor_id, usuario_id, data, observacoes=""):
        self.fornecedor_id = fornecedor_id
        self.usuario_id = usuario_id
        self.data = data
        self.observacoes = observacoes
        self.confirmada = False
        self._itens = []

    @property
    def itens(self):
        return tuple(self._itens)

    def total(self):
        return dinheiro(sum((item.total() for item in self._itens), 0))

    def adicionar_item(self, item):
        if self.confirmada:
            raise CompraConfirmadaError("Essa compra já foi confirmada e não pode mais ser alterada.")
        self._itens.append(item)

    def editar_item(self, posicao, item):
        if self.confirmada:
            raise CompraConfirmadaError("Essa compra já foi confirmada e não pode mais ser alterada.")
        if not 0 <= posicao < len(self._itens):
            raise ItemNaoEncontradoError("Esse item não está na compra.")
        self._itens[posicao] = item

    def remover_item(self, posicao):
        if self.confirmada:
            raise CompraConfirmadaError("Essa compra já foi confirmada e não pode mais ser alterada.")
        if not 0 <= posicao < len(self._itens):
            raise ItemNaoEncontradoError("Esse item não está na compra.")
        del self._itens[posicao]

    def confirmar(self):
        if self.confirmada:
            raise CompraConfirmadaError("Essa compra já foi confirmada e não pode mais ser alterada.")
        if not self._itens:
            raise CompraSemItensError("Adicione pelo menos um item antes de confirmar a compra.")
        self.confirmada = True
