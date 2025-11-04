from django.shortcuts import render
from django.contrib.auth.models import Group
from .models import Reporte
from django.conf import settings
import oracledb
import logging

logger = logging.getLogger(__name__)

def gria_view(request):
    """
    Vista para el proyecto general, este es el Principal dashboard.
    Mostrará solo los reportes a los que el usuario tiene acceso.
    Carga la página principal de forma síncrona y los datos de las tarjetas de forma asíncrona.
    """
    # --- Lógica del Dashboard ---
    # La consulta a Oracle se ha movido a una vista de API para carga asíncrona.
    reporte, created = Reporte.objects.update_or_create(
        identificador='indicadores-gerencia',
        defaults={
            'nombre_visible': 'Indicadores de Gerencia',
            'app_origen': 'dashboardgria',
            'url_name': '', # URL no necesaria, la lógica está en la vista principal
            'descripcion': 'Visualiza los indicadores de gestión diaria y acumulada.',
            'icono_fa': 'fas fa-chart-bar',
            'activo': True,
            'es_descarga': False,
            'card_template': 'gria/cards/indicadores_gerencia.html',
            'orden': 1,
            'tamaño': 2
        }
    )
    if created:
        gerencia_group, _ = Group.objects.get_or_create(name='gerencia')
        comercial_group, _ = Group.objects.get_or_create(name='comercial')
        reporte.grupos_permitidos.add(gerencia_group, comercial_group)

    reportes_autorizados = []
    if request.user.is_authenticated:
        if request.user.is_superuser:
            reportes_autorizados = Reporte.objects.all().order_by('orden')
        else:
            grupo_del_usuario = request.user.groups.all()
            reportes_autorizados = Reporte.objects.filter(grupos_permitidos__in=grupo_del_usuario).distinct().order_by('orden')

    # El contexto ahora solo pasa los reportes autorizados.
    # Los datos de la tarjeta se cargarán vía API.
    context = {
        'reportes_autorizados': reportes_autorizados,
    }

    return render(request, 'gria/gria_dashboard.html', context)


def api_get_indicadores_gerencia(request):
    """
    Vista de API para obtener los datos de los indicadores de gerencia de forma asíncrona.
    """
    datos = []
    # Parámetro como texto, según solicitud de BBDD.
    agencia_id = request.GET.get('agencia_id', '0')
    try:
        db = settings.DATABASES['oracle']
        dsn = f"{db['HOST']}:{db['PORT']}/{db['NAME']}"
        with oracledb.connect(user=db['USER'], password=db['PASSWORD'], dsn=dsn) as conn:
            with conn.cursor() as cursor:
                ref_cursor_out = cursor.var(oracledb.CURSOR)
                cursor.callproc('SP_GESTIONDIARIA', [agencia_id, ref_cursor_out])
                result_cursor = ref_cursor_out.getvalue()
                
                # Imprimir el resultado crudo para depuración
                # print(f"Resultado crudo del cursor de Oracle: {result_cursor}")

                if result_cursor:
                    columnas = [col[0] for col in result_cursor.description]
                    filas = result_cursor.fetchall()
                    datos = [dict(zip(columnas, fila)) for fila in filas]
                    # print(f"Datos obtenidos: {datos}")
                    logger.info(f"Consulta API exitosa: {len(datos)} filas para agencia {agencia_id}")

    except Exception as e:
        logger.error(f"Error en API consultando Oracle para agencia {agencia_id}: {e}", exc_info=True)

    context = {
        'datos_gestion_diaria': datos
    }
    
    # Renderiza solo la tabla, no la página completa
    return render(request, 'gria/cards/partials/_indicadores_gerencia_table.html', context)
