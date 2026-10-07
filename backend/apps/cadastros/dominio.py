"""
Cadastros do ateliê: cor, categoria e material.
"""

import re

from apps.comum.erros import ErroDeNegocio

FORMATO_HEX = re.compile(r"#[0-9A-Fa-f]{6}")


class CorInvalidaError(ErroDeNegocio):
    """Código da cor fora do formato #RRGGBB."""


class Cor:
    def __init__(self, nome, codigo_hex=None):
        self.nome = nome.strip()
        if codigo_hex is not None and not FORMATO_HEX.fullmatch(codigo_hex):
            raise CorInvalidaError("O código da cor precisa ser no formato #RRGGBB, por exemplo #315A81.")
        self.codigo_hex = codigo_hex.upper() if codigo_hex is not None else None

    def rotulo(self):
        return self.nome
