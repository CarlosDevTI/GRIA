# myapp/urls.py
from django.urls import path
from .views import (
    DashboardSarcView, 
    DashboardSarcDataJsonView, 
    UploadParametrosRiesgoView, 
    descargar_plantilla_parametros,
    DashboardSarLView,
    DashboardSarLDataJsonView
)

urlpatterns = [
    #! URLs de SARC
    path('sarc/', DashboardSarcView.as_view(), name='dashboard_sarc'),
    path('sarc/data/', DashboardSarcDataJsonView.as_view(), name='dashboard_sarc_data_json'),

    #! URL de SARL
    path('sarl/', DashboardSarLView.as_view(), name='dashboard_sarl'),
    path('sarl/data/', DashboardSarLDataJsonView.as_view(), name='dashboard_sarl_data_json'),

    #! URLs genéricas de Riesgos
    path('parametros/upload/', UploadParametrosRiesgoView.as_view(), name='upload_parametros_riesgo'),
    path('parametros/plantilla/', descargar_plantilla_parametros, name='descargar_plantilla_parametros'),
]