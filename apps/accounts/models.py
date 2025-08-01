from django.db import models
from django.contrib.auth.models import User, Group

class Role(Group):
    """
    Un modelo Proxy para el modelo Group de Django.
    Esto nos permite registrar 'Roles' en el admin en lugar de 'Grupos'
    sin crear una nueva tabla en la base de datos.
    """
    class Meta:
        proxy = True # Esto indica que no se crea una nueva tabla solo se modifica
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

class Profile(models.Model):
    """
    Modelo de perfil para extender el modelo de Usuario de Django.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Puedes agregar más campos aquí en el futuro, como avatar, teléfono, etc.

    def __str__(self):
        return f'Perfil de {self.user.username}'
