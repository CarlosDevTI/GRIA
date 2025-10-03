from django.urls import path
from apps.dashboardgria import views


urlpatterns = [
    path('', views.gria_view, name='gria_dashboard'),
    # Aquí puedes agregar más rutas relacionadas con la aplicación gria
]