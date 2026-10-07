"""
Cadastros do ateliê: cor, categoria e material.
"""


class Cor:
    def __init__(self, nome, codigo_hex=None):
        self.nome = nome.strip()
        self.codigo_hex = codigo_hex.upper() if codigo_hex is not None else None

    def rotulo(self):
        return self.nome
