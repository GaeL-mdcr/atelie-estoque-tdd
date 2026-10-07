"""
Produção de uma peça: o material que ela usou e devolveu, quanto custou,
quando ficou pronta e se está na vitrine.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from apps.cadastros.dominio import Categoria, CategoriaIncompativelError
from apps.comum.erros import ValorObrigatorioError
from apps.comum.numeros import dinheiro, quantidade, texto_obrigatorio

USO = "U"
RETORNO = "R"


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
