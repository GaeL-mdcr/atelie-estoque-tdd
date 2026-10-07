from django.apps import AppConfig


class SincronizacaoConfig(AppConfig):
    # PUSH e PULL com o SQLite do celular. Reenviar a mesma operação não pode duplicar nada.
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sincronizacao"
    verbose_name = "Sincronização"
