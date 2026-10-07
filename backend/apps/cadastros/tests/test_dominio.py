"""
Testes dos cadastros: cor, categoria e material.
"""

from apps.cadastros.dominio import Cor


def deve_guardar_nome_limpo_e_hex_em_maiusculas():
    azul = Cor("  Azul ", "#315a81")
    assert azul.nome == "Azul"
    assert azul.codigo_hex == "#315A81"
    # A cor nunca aparece só pela bolinha: o nome vai junto.
    assert azul.rotulo() == "Azul"
