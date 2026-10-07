"""
Produção de uma peça: o material que ela usou e devolveu, quanto custou,
quando ficou pronta e se está na vitrine.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from apps.cadastros.dominio import Categoria, CategoriaIncompativelError
from apps.comum.erros import ErroDeNegocio, ValorObrigatorioError
from apps.comum.numeros import dinheiro, formatar, quantidade, texto_obrigatorio

USO = "U"
RETORNO = "R"


class RetornoExcedeUsoError(ErroDeNegocio):
    """Tentou devolver mais do que ainda pode voltar daquele uso."""


class UsoNaoEncontradoError(ErroDeNegocio):
    """O uso de origem não existe nesta produção (ou o id é de um retorno)."""


class VarianteDiferenteError(ErroDeNegocio):
    """Retorno indo para o estoque de outra cor."""


@dataclass(frozen=True)
class MovimentacaoMaterial:
    """Um uso (U) ou retorno (R) de material. Depois de criada, não muda mais."""

    tipo: str
    variante_id: int
    quantidade: Decimal
    custo_unitario: Decimal
    quando: datetime
    id_uso_origem: str | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


class Producao:
    def __init__(self, nome_peca, categoria, usuario_id, vl_mao_obra="0", vl_venda="0",
                 pasta_id=None, descricao=""):
        self.nome_peca = texto_obrigatorio(nome_peca, "nome da peça")
        if categoria.tipo != Categoria.PRODUCAO:
            raise CategoriaIncompativelError("Escolha uma categoria de produção, como Saia ou Vestido.")
        self.categoria = categoria
        self.usuario_id = usuario_id
        self.vl_mao_obra = dinheiro(vl_mao_obra)
        self.vl_venda = dinheiro(vl_venda)
        self.pasta_id = pasta_id
        self.descricao = descricao
        self._movimentacoes = []

    def registrar_uso(self, estoque, qtd, quando):
        if estoque.variante_id is None:
            raise ValorObrigatorioError("Informe de qual material e cor saiu o material.")
        qtd = quantidade(qtd)
        custo = estoque.registrar_saida(qtd)
        uso = MovimentacaoMaterial(USO, estoque.variante_id, qtd, custo, quando)
        self._movimentacoes.append(uso)
        return uso

    def movimentacoes(self):
        return tuple(self._movimentacoes)

    def registrar_retorno(self, id_uso_origem, estoque, qtd, quando):
        uso = self._uso(id_uso_origem)
        if estoque.variante_id != uso.variante_id:
            raise VarianteDiferenteError("O material tem que voltar para a mesma cor de onde saiu.")
        qtd = quantidade(qtd)
        devolvivel = self.quantidade_devolvivel(uso.id)
        if qtd > devolvivel:
            raise RetornoExcedeUsoError(f"Desse uso ainda podem voltar no máximo {formatar(devolvivel)}.")
        estoque.registrar_retorno(qtd, uso.custo_unitario)
        retorno = MovimentacaoMaterial(RETORNO, uso.variante_id, qtd, uso.custo_unitario, quando, uso.id)
        self._movimentacoes.append(retorno)
        return retorno

    def quantidade_devolvivel(self, id_uso):
        uso = self._uso(id_uso)
        devolvido = sum(
            (m.quantidade for m in self._movimentacoes if m.id_uso_origem == id_uso), Decimal("0")
        )
        return quantidade(uso.quantidade - devolvido)

    def custo_materiais(self):
        # Usos somam e retornos subtraem, cada um com o custo que ficou gravado nele.
        total = Decimal("0")
        for movimentacao in self._movimentacoes:
            valor = movimentacao.quantidade * movimentacao.custo_unitario
            total += valor if movimentacao.tipo == USO else -valor
        return dinheiro(total)

    def custo_total(self):
        return dinheiro(self.custo_materiais() + self.vl_mao_obra)

    def _uso(self, id_uso):
        for movimentacao in self._movimentacoes:
            if movimentacao.id == id_uso and movimentacao.tipo == USO:
                return movimentacao
        raise UsoNaoEncontradoError("Esse uso de material não foi encontrado nesta produção.")
