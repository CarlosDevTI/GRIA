from django.contrib import admin
from django.urls import path
from django.urls import include, path
from apps.gria import views
from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView

urlpatterns = [
    # 1. La raíz del sitio redirige al login.
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False), name='index'),
    # 2. Incluimos las URLs de autenticación.
    path('accounts/', include('apps.accounts.urls')),
    # 3. Protegemos las vistas principales y las anidamos.
    path('gria/', login_required(views.gria_view), name='gria_dashboard'),
    path('gria/fondeos/', include('apps.fondeos.urls')),
    path('gria/risk/', include('apps.risk.urls')),
    path('admin/', admin.site.urls),
]
