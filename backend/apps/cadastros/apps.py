from django.apps import AppConfig


class CadastrosConfig(AppConfig):
    # Material, Cor, a variante Material + Cor, Categoria, Unidade de medida e Fornecedor.
    # É a base de tudo: compra, estoque e produção dependem desses cadastros.
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cadastros"
    verbose_name = "Cadastros"
