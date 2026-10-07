"""
Testes da produção (a peça): uso e retorno de material, custos, conclusão,
reabertura e vitrine. Os números são os da Saia midi da Referência SQL.
"""

from datetime import datetime, timedelta, timezone

import pytest

from apps.cadastros.dominio import Categoria, CategoriaIncompativelError
from apps.comum.erros import ValorObrigatorioError
from apps.producoes.dominio import Producao

SAIA = Categoria("Saia", "P")
T1 = datetime(2026, 9, 18, 17, 15, tzinfo=timezone.utc)
T2 = T1 + timedelta(minutes=5)


@pytest.fixture
def saia():
    return Producao("Saia midi", SAIA, usuario_id=1, vl_mao_obra="60", vl_venda="220")


def deve_criar_producao_sem_pasta_e_so_com_categoria_de_producao(saia):
    assert saia.pasta_id is None
    with pytest.raises(CategoriaIncompativelError):
        Producao("Saia midi", Categoria("Tecido", "M"), 1)
    with pytest.raises(ValorObrigatorioError):
        Producao("  ", SAIA, 1)
