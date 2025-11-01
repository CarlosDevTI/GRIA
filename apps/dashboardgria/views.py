from django.shortcuts import render
from django.contrib.auth.models import Group
from .models import Reporte

def gria_view(request):
    """
    Vista para el proyecto general, este es el Principal dashboard.
    Mostrará solo los reportes a los que el usuario tiene acceso.
    """
    # Crear el reporte de Indicadores de Gerencia si no existe
    reporte, created = Reporte.objects.get_or_create(
        identificador='indicadores-gerencia',
        defaults={
            'nombre_visible': 'Indicadores de Gerencia',
            'app_origen': 'gerencia',
            'url_name': 'indicadores_gerencia',
            'descripcion': 'Visualiza los indicadores de gestión diaria y acumulada.',
            'icono_fa': 'fas fa-chart-bar',
            'activo': True,
            'es_descarga': False,
            'card_template': 'gria/cards/indicadores_gerencia.html'
        }
    )

    # Asignar a grupos
    if created:
        gerencia_group, _ = Group.objects.get_or_create(name='gerencia')
        comercial_group, _ = Group.objects.get_or_create(name='comercial')
        reporte.grupos_permitidos.add(gerencia_group, comercial_group)

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