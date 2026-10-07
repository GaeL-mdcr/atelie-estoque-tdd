"""
Testes dos cadastros: cor, categoria e material.
"""

from decimal import Decimal

import pytest

from apps.cadastros.dominio import (
    Categoria,
    CategoriaIncompativelError,
    Cor,
    CorInvalidaError,
    Material,
    VarianteDuplicadaError,
    VarianteNaoEncontradaError,
)
from apps.comum.erros import ValorInvalidoError, ValorObrigatorioError


def deve_guardar_nome_limpo_e_hex_em_maiusculas():
    azul = Cor("  Azul ", "#315a81")
    assert azul.nome == "Azul"
    assert azul.codigo_hex == "#315A81"
    # A cor nunca aparece só pela bolinha: o nome vai junto.
    assert azul.rotulo() == "Azul"


def deve_aceitar_cor_sem_hex():
    assert Cor("Branco").codigo_hex is None


# "#315A81\n" pega uma pegadinha do Python: o $ da regex aceita uma quebra de linha no fim.
@pytest.mark.parametrize("codigo", ["azul", "#12345", "#GGGGGG", "315A81", "#315A81\n"])
def nao_deve_aceitar_hex_fora_do_formato(codigo):
    with pytest.raises(CorInvalidaError):
        Cor("Azul", codigo)


def nao_deve_aceitar_nome_vazio():
    with pytest.raises(ValorObrigatorioError):
        Cor("   ")
    with pytest.raises(ValorObrigatorioError):
        Categoria("", "M")


# M = categoria de material (Tecido), P = categoria de produção (Saia). Não existe outro tipo.
def deve_criar_categoria_de_material_ou_producao():
    tecido = Categoria(" Tecido ", "M")
    assert tecido.nome == "Tecido"
    assert tecido.tipo == "M"
    assert Categoria("Saia", "P").tipo == Categoria.PRODUCAO
    with pytest.raises(ValorInvalidoError):
        Categoria("Saia", "X")


def deve_arquivar_e_reativar_cor():
    azul = Cor("Azul")
    assert azul.ativo is True
    azul.arquivar()
    assert azul.ativo is False
    azul.reativar()
    assert azul.ativo is True


# ---------- Material ----------

TECIDO = Categoria("Tecido", "M")
SAIA = Categoria("Saia", "P")
METRO = 1


def deve_criar_material_ativo_com_categoria_de_material():
    oxford = Material("Tecido Oxford", TECIDO, METRO)
    assert oxford.nome == "Tecido Oxford"
    assert oxford.ativo is True
    assert oxford.cores() == []


def nao_deve_aceitar_categoria_de_producao():
    with pytest.raises(CategoriaIncompativelError):
        Material("Tecido Oxford", SAIA, METRO)


# Cada cor do material tem o seu estoque: saldo, custo e mínimo próprios.
def deve_adicionar_cor_com_estoque_proprio():
    oxford = Material("Tecido Oxford", TECIDO, METRO)
    azul = oxford.adicionar_cor(Cor("Azul"), "5", "10", "7")
    assert azul.saldo == Decimal("10.000")
    assert azul.custo_medio == Decimal("7.00")
    assert azul.qtd_estoque_minimo == Decimal("5.000")
    assert oxford.cores() == ["Azul"]


# "Azul" e " azul " são a mesma cor para a dona do ateliê, então a segunda é recusada.
def nao_deve_repetir_a_mesma_cor_no_material():
    oxford = Material("Tecido Oxford", TECIDO, METRO)
    oxford.adicionar_cor(Cor("Azul"))
    with pytest.raises(VarianteDuplicadaError):
        oxford.adicionar_cor(Cor(" azul "))
    assert oxford.cores() == ["Azul"]


# Comprar Branco não pode mexer no saldo do Azul (RN-T10).
def deve_manter_estoque_separado_por_cor():
    oxford = Material("Tecido Oxford", TECIDO, METRO)
    oxford.adicionar_cor(Cor("Azul"), qtd_inicial="10", vl_unitario_inicial="7")
    oxford.adicionar_cor(Cor("Branco"))
    oxford.estoque_da_cor(Cor("Branco")).registrar_entrada("10", "20")
    assert oxford.estoque_da_cor(Cor("Azul")).saldo == Decimal("10.000")
    assert oxford.estoque_da_cor(Cor("Branco")).saldo == Decimal("10.000")


def nao_deve_achar_estoque_de_cor_nao_cadastrada():
    oxford = Material("Tecido Oxford", TECIDO, METRO)
    oxford.adicionar_cor(Cor("Azul"))
    with pytest.raises(VarianteNaoEncontradaError):
        oxford.estoque_da_cor(Cor("Verde"))
