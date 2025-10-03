from django.shortcuts import render
from .models import Reporte

# Create your views here.
def gria_view(request):
    """
    Vista para el proyecto general, este es el Principal dashboard.
    Mostrará solo los reportes a los que el usuario tiene acceso.
    """
    reportes_autorizados = []
    if request.user.is_authenticated:
        if request.user.is_superuser:
            reportes_autorizados = Reporte.objects.all()
        else:
            grupo_del_usuario = request.user.groups.all()
            reportes_autorizados = Reporte.objects.filter(grupos_permitidos__in=grupo_del_usuario).distinct()

    context = {
        'reportes_autorizados': reportes_autorizados
    }

    return render(request, 'gria/gria_dashboard.html', context)