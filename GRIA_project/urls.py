from django.contrib import admin
from django.urls import path, include
from apps.gria import views as gria_views
from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False), name='index'),
    path('accounts/', include('apps.accounts.urls')),
    path('admin/', admin.site.urls),

    # Rutas de la aplicación principal
    path('gria/', login_required(gria_views.gria_view), name='gria_dashboard'),
    path('gria/fondeos/', include('apps.fondeos.urls')),
    path('gria/risk/', include('apps.risk.urls')),
    path('gria/apre/', include('apps.apre.urls')),
]