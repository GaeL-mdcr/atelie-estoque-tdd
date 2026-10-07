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
from apps.comum.numeros import dinheiro, quantidade, texto_obrigatorio

USO = "U"
RETORNO = "R"


class RetornoExcedeUsoError(ErroDeNegocio):
    """Tentou devolver mais do que ainda pode voltar daquele uso."""


class UsoNaoEncontradoError(ErroDeNegocio):
    """O uso de origem não existe nesta produção (ou o id é de um retorno)."""


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
        qtd = quantidade(qtd)
        devolvivel = self.quantidade_devolvivel(uso.id)
        if qtd > devolvivel:
            texto = format(devolvivel.normalize(), "f").replace(".", ",")
            raise RetornoExcedeUsoError(f"Desse uso ainda podem voltar no máximo {texto}.")
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

    def _uso(self, id_uso):
        for movimentacao in self._movimentacoes:
            if movimentacao.id == id_uso and movimentacao.tipo == USO:
                return movimentacao
        raise UsoNaoEncontradoError("Esse uso de material não foi encontrado nesta produção.")
