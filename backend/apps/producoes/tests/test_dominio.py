"""
Testes da produção (a peça): uso e retorno de material, custos, conclusão,
reabertura e vitrine. Os números são os da Saia midi da Referência SQL.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from apps.cadastros.dominio import Categoria, CategoriaIncompativelError
from apps.comum.erros import ValorObrigatorioError
from apps.estoque.dominio import EstoqueVariante
from apps.producoes.dominio import Producao

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
