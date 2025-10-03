from django.contrib import admin
from django.urls import path, include
from apps.dashboardgria import views as gria_views
from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False), name='index'),
    path('accounts/', include('apps.accounts.urls')),
    path('admin/', admin.site.urls),

    # Rutas de la aplicación principal
    path('gria/', login_required(gria_views.gria_view), name='gria_dashboard'),
    path('gria/comercial/', include('apps.comercial.urls')),
    path('gria/riesgos/', include('apps.riesgos.urls')),
    path('gria/financiera/', include('apps.financiera.urls')),
    path('gria/cumplimiento/', include('apps.cumplimiento.urls')),  # Nueva ruta para la app cumplimiento
]