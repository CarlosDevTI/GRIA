from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from .models import Profile, Role

# Desregistrar el modelo Group base
admin.site.unregister(Group)

@admin.register(Role)
class RoleAdmin(BaseGroupAdmin):
    """
    Admin para nuestro modelo Proxy 'Role'. Se verá y actuará como el admin de Group.
    """
    pass

class ProfileInline(admin.StackedInline):
    """Define un admin inline para el Perfil que se mostrará en el User admin."""
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfiles'

class CustomUserAdmin(BaseUserAdmin):
    """Extiende el UserAdmin para incluir el Profile."""
    inlines = (ProfileInline,)

# Desregistrar el UserAdmin base y registrar el nuestro personalizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
