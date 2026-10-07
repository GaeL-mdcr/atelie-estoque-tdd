"""
Testes da produção (a peça): uso e retorno de material, custos, conclusão,
reabertura e vitrine. Os números são os da Saia midi da Referência SQL.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from apps.cadastros.dominio import Categoria, CategoriaIncompativelError
from apps.comum.erros import ValorObrigatorioError
from apps.estoque.dominio import EstoqueVariante, SaldoInsuficienteError
from apps.producoes.dominio import Producao, RetornoExcedeUsoError

SAIA = Categoria("Saia", "P")
T1 = datetime(2026, 9, 18, 17, 15, tzinfo=timezone.utc)
T2 = T1 + timedelta(minutes=5)


@pytest.fixture
def saia():
    return Producao("Saia midi", SAIA, usuario_id=1, vl_mao_obra="60", vl_venda="220")


@pytest.fixture
def azul():
    """Tecido Oxford Azul depois da compra: 50 m a R$ 4,60."""
    return EstoqueVariante("50", "4.60", variante_id=10)


def deve_criar_producao_sem_pasta_e_so_com_categoria_de_producao(saia):
    assert saia.pasta_id is None
    with pytest.raises(CategoriaIncompativelError):
        Producao("Saia midi", Categoria("Tecido", "M"), 1)
    with pytest.raises(ValorObrigatorioError):
        Producao("  ", SAIA, 1)


# O uso grava o custo médio do momento (RN-T12) e baixa o estoque daquela cor.
def deve_registrar_uso_com_o_custo_medio_vigente(saia, azul):
    uso = saia.registrar_uso(azul, "3", T1)
    assert uso.tipo == "U"
    assert uso.variante_id == 10
    assert uso.quantidade == Decimal("3.000")
    assert uso.custo_unitario == Decimal("4.60")
    assert uso.quando == T1
    assert uso.id_uso_origem is None
    assert azul.saldo == Decimal("47.000")
    with pytest.raises(ValorObrigatorioError):
        saia.registrar_uso(EstoqueVariante("5", "1"), "1", T1)


# Compra nova muda a média do estoque, mas o custo que ficou gravado no uso não muda.
def deve_manter_o_custo_do_uso_quando_chega_compra_nova(saia, azul):
    uso = saia.registrar_uso(azul, "3", T1)
    azul.registrar_entrada("10", "100")
    assert uso.custo_unitario == Decimal("4.60")


def nao_deve_usar_mais_que_o_saldo(saia):
    pouco = EstoqueVariante("2", "5", variante_id=10)
    with pytest.raises(SaldoInsuficienteError):
        saia.registrar_uso(pouco, "2.5", T1)
    assert saia.movimentacoes() == ()


# O retorno aponta para o uso de origem e volta com o custo dele. O uso não é apagado.
def deve_registrar_retorno_apontando_para_o_uso(saia, azul):
    uso = saia.registrar_uso(azul, "3", T1)
    retorno = saia.registrar_retorno(uso.id, azul, "0.5", T2)
    assert retorno.tipo == "R"
    assert retorno.id_uso_origem == uso.id
    assert retorno.custo_unitario == Decimal("4.60")
    assert retorno.quantidade == Decimal("0.500")
    assert azul.saldo == Decimal("47.500")
    assert saia.movimentacoes() == (uso, retorno)


def deve_calcular_quanto_ainda_pode_voltar(saia, azul):
    uso = saia.registrar_uso(azul, "3", T1)
    saia.registrar_retorno(uso.id, azul, "0.5", T2)
    assert saia.quantidade_devolvivel(uso.id) == Decimal("2.500")


# Dois retornos que, somados, passam do usado: o segundo é recusado e o estoque não muda.
def nao_deve_devolver_mais_que_o_devolvivel(saia, azul):
    uso = saia.registrar_uso(azul, "3", T1)
    with pytest.raises(RetornoExcedeUsoError):
        saia.registrar_retorno(uso.id, azul, "3.5", T2)
    saia.registrar_retorno(uso.id, azul, "2.5", T2)
    with pytest.raises(RetornoExcedeUsoError):
        saia.registrar_retorno(uso.id, azul, "0.501", T2)
    assert azul.saldo == Decimal("49.500")
    assert len(saia.movimentacoes()) == 2


# Decisão D05 com dois custos diferentes: o retorno volta com o custo do SEU uso, não com a média de hoje.
def deve_devolver_com_o_custo_do_uso_de_origem(saia):
    azul = EstoqueVariante("10", "4", variante_id=10)
    uso1 = saia.registrar_uso(azul, "2", T1)          # R$ 4,00
    azul.registrar_entrada("10", "100")               # (8 × 4 + 100) ÷ 18 = R$ 7,33
    uso2 = saia.registrar_uso(azul, "2", T2)          # R$ 7,33
    retorno = saia.registrar_retorno(uso1.id, azul, "1", T2)
    assert uso2.custo_unitario == Decimal("7.33")
    assert retorno.custo_unitario == Decimal("4.00")
    assert azul.saldo == Decimal("17.000")
    assert azul.custo_medio == Decimal("7.13")        # (16 × 7,33 + 1 × 4,00) ÷ 17
