"""
Comportamento de "arquivar" usado por Material, Cor e Fornecedor (decisão D07).

Quem herda precisa fazer self.ativo = True no próprio __init__.
"""


class Arquivavel:
    ativo: bool

    def arquivar(self):
        self.ativo = False

    def reativar(self):
        self.ativo = True
