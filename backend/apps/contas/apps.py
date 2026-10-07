from django.apps import AppConfig


class ContasConfig(AppConfig):
    # Aqui vai morar o usuário do sistema (Usuario do Lógico_1) e o login por JWT.
    # O modelo de usuário precisa nascer antes da primeira migration, senão dá dor de cabeça depois.
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.contas"
    verbose_name = "Contas e acesso"
