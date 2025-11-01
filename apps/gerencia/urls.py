from django.urls import path
from . import views

urlpatterns = [
    path('indicadores/<int:agencia_id>/', views.indicadores_gerencia, name='indicadores_gerencia'),
]
