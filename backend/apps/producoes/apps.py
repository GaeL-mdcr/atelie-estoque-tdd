from django.apps import AppConfig


class ProducoesConfig(AppConfig):
    # Peças produzidas, pastas, imagens, conclusão, reabertura com histórico e publicação.
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.producoes"
    verbose_name = "Produções"
