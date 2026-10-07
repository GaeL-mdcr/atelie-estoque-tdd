"""
Testes dos cadastros: cor, categoria e material.
"""

import pytest

from apps.cadastros.dominio import Cor, CorInvalidaError


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
