from django.contrib.auth import views as auth_views, login
from django.urls import reverse_lazy
from django.shortcuts import resolve_url
from django.http import HttpResponseRedirect

class CustomLoginView(auth_views.LoginView):
    template_name = 'accounts/registration/login.html'

    def form_valid(self, form):
        user = form.get_user()
        
        # --- DEBUGGING con print --- #
        print(f"[DEBUG] Intentando iniciar sesión para el usuario: {user.username}")
        print(f"[DEBUG] Valor de user.last_login: {repr(user.last_login)}")
        print(f"[DEBUG] Resultado de (user.last_login is None): {user.last_login is None}")
        # --- FIN DEBUGGING --- #

        is_first_login = user.last_login is None

        login(self.request, user)

        if is_first_login:
            return HttpResponseRedirect(reverse_lazy('password_change'))
        
        # Redirigir al dashboard correcto
        return HttpResponseRedirect(resolve_url('gria_dashboard'))
