"""
Estoque de uma variante (material + cor): saldo e custo médio ponderado.

Cada cor tem o seu: mexer no Azul não muda o Branco do mesmo tecido.
"""

from apps.comum.erros import ErroDeNegocio
from apps.comum.numeros import decimal_de, dinheiro, quantidade


class SaldoInsuficienteError(ErroDeNegocio):
    """Pediu mais material do que tem no estoque daquela cor."""

    def __init__(self, disponivel):
        self.disponivel = disponivel
        texto = format(disponivel.normalize(), "f").replace(".", ",")
        super().__init__(f"Não tem material suficiente. Disponível: {texto}.")


class EstoqueVariante:
    def __init__(self, qtd_inicial="0", vl_unitario_inicial="0", qtd_estoque_minimo="0"):
        self._saldo = quantidade(qtd_inicial)
        self._custo_medio = dinheiro(vl_unitario_inicial)

    @property
    def saldo(self):
        return self._saldo

    @property
    def custo_medio(self):
        return self._custo_medio

    def registrar_entrada(self, qtd, custo_total):
        qtd = quantidade(qtd)
        valor_em_estoque = self._saldo * self._custo_medio + decimal_de(custo_total)
        self._saldo = quantidade(self._saldo + qtd)
        self._custo_medio = dinheiro(valor_em_estoque / self._saldo)

    def registrar_saida(self, qtd):
        qtd = quantidade(qtd)
        if qtd > self._saldo:
            raise SaldoInsuficienteError(self._saldo)
        self._saldo = quantidade(self._saldo - qtd)
        return self._custo_medio

    def registrar_retorno(self, qtd, custo_unitario):
        qtd = quantidade(qtd)
        valor_em_estoque = self._saldo * self._custo_medio + qtd * decimal_de(custo_unitario)
        self._saldo = quantidade(self._saldo + qtd)
        self._custo_medio = dinheiro(valor_em_estoque / self._saldo)
