from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def role_required(allowed_roles=[]):
    """
    Decorador para vistas que verifica si un usuario tiene uno de los roles permitidos.
    Un superusuario siempre tiene acceso.
    Ejemplo de uso: @role_required(allowed_roles=['Admin', 'Editor'])
    """
    def check_roles(user):
        if user.is_superuser:
            return True
        # Comprueba si el usuario pertenece a alguno de los grupos (roles) permitidos.
        if user.groups.filter(name__in=allowed_roles).exists():
            return True
        # Si no tiene el rol, lanza un error de Permiso Denegado (403 Forbidden)
        raise PermissionDenied
    
    # user_passes_test se encarga de la redirección al login si no está autenticado
    return user_passes_test(check_roles)