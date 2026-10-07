from django.apps import AppConfig


class MovimentacoesConfig(AppConfig):
    # Uso (U) e retorno (R) de material em uma produção.
    # Retorno nunca apaga o uso: é um lançamento novo que aponta para o uso de origem.
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.movimentacoes"
    verbose_name = "Uso e retorno de materiais"
