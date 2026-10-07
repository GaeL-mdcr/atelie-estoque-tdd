"""
Testes do próprio ambiente, não de regra de negócio.

Servem só para garantir que o pytest enxerga o Django e que os módulos do
ateliê estão registrados. Se algum destes quebrar, o problema é de configuração,
não de código de produção.
"""

from django.conf import settings

MODULOS_DO_ATELIE = [
    "apps.contas",
    "apps.cadastros",
    "apps.conversoes",
    "apps.compras",
    "apps.estoque",
    "apps.producoes",
    "apps.movimentacoes",
    "apps.sincronizacao",
    "apps.vitrine",
]


def deve_registrar_todos_os_modulos_do_atelie():
    for modulo in MODULOS_DO_ATELIE:
        assert modulo in settings.INSTALLED_APPS, f"{modulo} ficou de fora do INSTALLED_APPS"


def deve_usar_fuso_de_cuiaba_e_portugues():
    assert settings.TIME_ZONE == "America/Cuiaba"
    assert settings.LANGUAGE_CODE == "pt-br"
    assert settings.USE_TZ is True


def deve_exigir_login_por_jwt_na_api():
    config = settings.REST_FRAMEWORK
    assert "rest_framework_simplejwt.authentication.JWTAuthentication" in config["DEFAULT_AUTHENTICATION_CLASSES"]
    assert "rest_framework.permissions.IsAuthenticated" in config["DEFAULT_PERMISSION_CLASSES"]
