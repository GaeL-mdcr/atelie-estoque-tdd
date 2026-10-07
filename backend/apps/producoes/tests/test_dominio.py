"""
Testes da produção (a peça): uso e retorno de material, custos, conclusão,
reabertura e vitrine. Os números são os da Saia midi da Referência SQL.
"""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from apps.cadastros.dominio import Categoria, CategoriaIncompativelError
from apps.comum.erros import ValorInvalidoError, ValorObrigatorioError
from apps.estoque.dominio import EstoqueVariante, SaldoInsuficienteError
from apps.producoes.dominio import (
    Producao,
    ProducaoConcluidaError,
    ProducaoNaoConcluidaError,
    RetornoExcedeUsoError,
    UsoNaoEncontradoError,
    VarianteDiferenteError,
)

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


# Só dá para devolver de um uso desta produção; um retorno não serve de origem.
def nao_deve_devolver_uso_inexistente_nem_retorno(saia, azul):
    uso = saia.registrar_uso(azul, "3", T1)
    retorno = saia.registrar_retorno(uso.id, azul, "0.5", T2)
    with pytest.raises(UsoNaoEncontradoError):
        saia.registrar_retorno("nao-existe", azul, "0.5", T2)
    with pytest.raises(UsoNaoEncontradoError):
        saia.registrar_retorno(retorno.id, azul, "0.1", T2)
    assert azul.saldo == Decimal("47.500")


# Tecido que saiu do Azul não pode voltar para o estoque do Branco.
def nao_deve_devolver_para_outra_cor(saia, azul):
    uso = saia.registrar_uso(azul, "3", T1)
    branco = EstoqueVariante("5", "3", variante_id=11)
    with pytest.raises(VarianteDiferenteError):
        saia.registrar_retorno(uso.id, branco, "1", T2)
    assert azul.saldo == Decimal("47.000")
    assert branco.saldo == Decimal("5.000")


# ---------- Custos, conclusão, reabertura e vitrine ----------

CONCLUSAO = date(2026, 10, 20)


# Saia midi: usou 3 m e devolveu 0,5 m a R$ 4,60 → 2,5 × 4,60 = R$ 11,50; com R$ 60 de mão de obra, R$ 71,50.
def deve_calcular_os_custos_da_saia_midi(saia, azul):
    uso = saia.registrar_uso(azul, "3", T1)
    saia.registrar_retorno(uso.id, azul, "0.5", T2)
    assert saia.custo_materiais() == Decimal("11.50")
    assert saia.custo_total() == Decimal("71.50")


def deve_ter_custo_so_de_mao_de_obra_sem_movimentacoes(saia):
    assert saia.custo_materiais() == Decimal("0.00")
    assert saia.custo_total() == Decimal("60.00")


# Peça pronta não recebe nem devolve material (RN-T15).
def deve_bloquear_uso_e_retorno_depois_de_concluir(saia, azul):
    uso = saia.registrar_uso(azul, "3", T1)
    saia.concluir(CONCLUSAO)
    assert saia.concluida is True
    assert saia.dt_finalizacao == CONCLUSAO
    with pytest.raises(ProducaoConcluidaError):
        saia.registrar_uso(azul, "1", T2)
    with pytest.raises(ProducaoConcluidaError):
        saia.registrar_retorno(uso.id, azul, "1", T2)
    assert azul.saldo == Decimal("47.000")


def nao_deve_concluir_duas_vezes(saia):
    saia.concluir(CONCLUSAO)
    with pytest.raises(ProducaoConcluidaError):
        saia.concluir(date(2026, 10, 21))
    assert saia.dt_finalizacao == CONCLUSAO


# Reabrir guarda quem, quando e por quê (decisão D06), e a peça volta a aceitar material.
def deve_reabrir_com_motivo_e_guardar_historico(saia, azul):
    saia.concluir(CONCLUSAO)
    evento = saia.reabrir("Cliente pediu ajuste na barra", usuario_id=1, quando=T2)
    assert saia.concluida is False
    assert saia.dt_finalizacao is None
    assert evento.motivo == "Cliente pediu ajuste na barra"
    assert evento.usuario_id == 1
    assert evento.quando == T2
    assert evento.dt_finalizacao_anterior == CONCLUSAO
    saia.registrar_uso(azul, "1", T2)
    saia.concluir(date(2026, 10, 25))
    saia.reabrir("Trocar botões", usuario_id=1, quando=T2)
    assert [e.motivo for e in saia.historico_reaberturas()] == ["Cliente pediu ajuste na barra", "Trocar botões"]


def nao_deve_reabrir_sem_motivo_ou_sem_estar_concluida(saia):
    with pytest.raises(ProducaoNaoConcluidaError):
        saia.reabrir("Ajuste", usuario_id=1, quando=T2)
    saia.concluir(CONCLUSAO)
    with pytest.raises(ValorObrigatorioError):
        saia.reabrir("   ", usuario_id=1, quando=T2)
    assert saia.concluida is True
    assert saia.historico_reaberturas() == ()


# Vitrine é só para peça pronta, e a publicação é manual (RN-T17).
def deve_publicar_so_producao_concluida(saia):
    with pytest.raises(ProducaoNaoConcluidaError):
        saia.publicar_na_vitrine()
    assert saia.publicada is False
    saia.concluir(CONCLUSAO)
    saia.publicar_na_vitrine()
    assert saia.publicada is True
    saia.retirar_da_vitrine()
    assert saia.publicada is False


# Decisão D15: peça reaberta está em andamento de novo, então sai da vitrine sozinha.
def deve_tirar_da_vitrine_quando_reabrir(saia):
    saia.concluir(CONCLUSAO)
    saia.publicar_na_vitrine()
    saia.reabrir("Cliente pediu ajuste na barra", usuario_id=1, quando=T2)
    assert saia.publicada is False


# A vitrine só vê o que a cliente pode ver: nada de custo, fornecedor ou estoque.
# (As imagens entram na Fase 2, quando existir a tabela Imagem_Producao.)
def deve_expor_so_os_dados_publicos(saia, azul):
    saia.registrar_uso(azul, "3", T1)
    assert saia.dados_publicos() == {
        "nome_peca": "Saia midi",
        "categoria": "Saia",
        "descricao": "",
        "vl_venda": Decimal("220.00"),
    }


# RN-T01 vale para a produção também: mão de obra e preço de venda não podem ser negativos.
def nao_deve_aceitar_mao_de_obra_ou_venda_negativa():
    with pytest.raises(ValorInvalidoError):
        Producao("Saia midi", SAIA, 1, vl_mao_obra="-60")
    with pytest.raises(ValorInvalidoError):
        Producao("Saia midi", SAIA, 1, vl_venda="-1")
