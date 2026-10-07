from django.apps import AppConfig


class ComprasConfig(AppConfig):
    # Compra com um ou vários itens. Ou grava tudo, ou não grava nada.
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.compras"
    verbose_name = "Compras"
