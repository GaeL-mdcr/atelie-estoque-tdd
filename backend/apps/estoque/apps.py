from django.apps import AppConfig


class EstoqueConfig(AppConfig):
    # Saldo e custo médio de cada material em cada cor, mais o histórico de entradas e saídas.
    # Ninguém digita saldo na mão: ele sai das compras, usos e retornos.
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.estoque"
    verbose_name = "Estoque"
