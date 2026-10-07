from django.contrib import admin
from django.urls import path

# As rotas da API (/api/v1/...) vão entrando aqui conforme cada funcionalidade
# nascer de um teste. Por enquanto só o admin do Django.
urlpatterns = [
    path("admin/", admin.site.urls),
]
