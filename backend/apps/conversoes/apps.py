from django.apps import AppConfig


class ConversoesConfig(AppConfig):
    # Equivalência entre a unidade da compra e a unidade do estoque de cada material.
    # Exemplo do dia a dia: 1 rolo = 50 metros.
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.conversoes"
    verbose_name = "Conversões de unidade"
