from django.urls import path
from apps.dashboardgria import views


urlpatterns = [
    path('', views.gria_view, name='gria_dashboard'),
    path('api/indicadores-gerencia/', views.api_get_indicadores_gerencia, name='api_get_indicadores_gerencia'),
    # Aquí puedes agregar más rutas relacionadas con la aplicación gria
]