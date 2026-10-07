from django.apps import AppConfig


class VitrineConfig(AppConfig):
    # Reservado para o site público. Não será implementado agora,
    # mas já tem lugar próprio para não misturar dados internos com o que vai para fora.
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.vitrine"
    verbose_name = "Vitrine"
