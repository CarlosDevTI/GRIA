# myapp/urls.py
from django.urls import path
from .views import (
    DashboardSarcView, DashboardSarcDataJsonView, UploadParametrosRiesgoView,
)

urlpatterns = [
    path('sarc/', DashboardSarcView.as_view(), name='dashboard_sarc'),
    path('sarc/data/', DashboardSarcDataJsonView.as_view(), name='dashboard_sarc_data_json'),
    path('sarc/upload/', UploadParametrosRiesgoView.as_view(), name='upload_parametros_riesgo'),
]
