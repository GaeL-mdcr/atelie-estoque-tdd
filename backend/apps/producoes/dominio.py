"""
Produção de uma peça: o material que ela usou e devolveu, quanto custou,
quando ficou pronta e se está na vitrine.
"""

from apps.cadastros.dominio import Categoria, CategoriaIncompativelError
from apps.comum.numeros import dinheiro, texto_obrigatorio


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
