from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import CustomLoginView

urlpatterns = [
    # URL para el login usando la vista personalizada
    path('login/', CustomLoginView.as_view(), name='login'),

    # URL para el logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # URL para el cambio de contraseña
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/changepassword/cambiar_contrasena.html',
        success_url=reverse_lazy('gria_dashboard') # Redirigir al dashboard tras el éxito
    ), name='password_change'),

    # Vista de confirmación de cambio de contraseña (aunque no se use, es buena práctica tenerla)
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/changepassword/cambiar_contrasena_done.html'
    ), name='password_change_done'),
]