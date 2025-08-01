from django.urls import path
from django.contrib.auth import views as auth_views
# from .views import dashboard_redirect_view

urlpatterns = [
    # URL para el login
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/registration/login.html'
    ), name='login'),

    # URL para el logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # URL para el cambio de contraseña
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/changepassword/cambiar_contrasena.html',
        success_url='/accounts/password_change/done/' # URL a la que se redirige tras el éxito
    ), name='password_change'),

    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/changepassword/cambiar_contrasena_done.html'
    ), name='password_change_done'),
]