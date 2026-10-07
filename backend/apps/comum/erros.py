"""
Erros de regra de negócio do ateliê.

Todos herdam de ErroDeNegocio, e a mensagem é escrita para a dona do ateliê
ler na tela, não para o programador.
"""


class ErroDeNegocio(Exception):
    """Base de todo erro de regra do ateliê."""


class ValorInvalidoError(ErroDeNegocio):
    """Valor que não serve: negativo, texto no lugar de número, float..."""


class ValorObrigatorioError(ErroDeNegocio):
    """Campo que não pode ficar em branco."""


class QuantidadeInvalidaError(ErroDeNegocio):
    """Quantidade que precisa ser maior que zero e não é."""
