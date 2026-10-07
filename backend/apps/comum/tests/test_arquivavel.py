"""
Arquivar não é apagar: o material (ou a cor, o fornecedor) só some das listas
de escolha, e o histórico de compras e produções continua inteiro.
"""

from apps.comum.arquivavel import Arquivavel


class Coisa(Arquivavel):
    def __init__(self):
        self.ativo = True


def deve_arquivar_e_reativar():
    coisa = Coisa()
    coisa.arquivar()
    assert coisa.ativo is False
    coisa.reativar()
    assert coisa.ativo is True
