"""
Cadastros do ateliê: cor, categoria e material.
"""

import re

from apps.comum.arquivavel import Arquivavel
from apps.comum.erros import ErroDeNegocio, ValorInvalidoError
from apps.comum.numeros import texto_obrigatorio

FORMATO_HEX = re.compile(r"#[0-9A-Fa-f]{6}")


class CorInvalidaError(ErroDeNegocio):
    """Código da cor fora do formato #RRGGBB."""


class CategoriaIncompativelError(ErroDeNegocio):
    """Categoria de produção usada num material, ou o contrário."""


class Cor(Arquivavel):
    def __init__(self, nome, codigo_hex=None):
        self.ativo = True
        self.nome = texto_obrigatorio(nome, "nome da cor")
        if codigo_hex is not None and not FORMATO_HEX.fullmatch(codigo_hex):
            raise CorInvalidaError("O código da cor precisa ser no formato #RRGGBB, por exemplo #315A81.")
        self.codigo_hex = codigo_hex.upper() if codigo_hex is not None else None

    def rotulo(self):
        return self.nome


class Categoria:
    MATERIAL = "M"
    PRODUCAO = "P"

    def __init__(self, nome, tipo):
        self.nome = texto_obrigatorio(nome, "nome da categoria")
        if tipo not in (self.MATERIAL, self.PRODUCAO):
            raise ValorInvalidoError("A categoria precisa ser de material (M) ou de produção (P).")
        self.tipo = tipo


class Material(Arquivavel):
    def __init__(self, nome, categoria, unidade_estoque_id, descricao=""):
        self.ativo = True
        self.nome = nome
        if categoria.tipo != Categoria.MATERIAL:
            raise CategoriaIncompativelError("Escolha uma categoria de material, como Tecido ou Linha.")
        self.categoria = categoria
        self.unidade_estoque_id = unidade_estoque_id
        self.descricao = descricao

    def cores(self):
        return []
