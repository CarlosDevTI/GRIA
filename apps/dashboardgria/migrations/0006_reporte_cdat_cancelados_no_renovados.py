from django.db import migrations


def create_cdat_cancelados_no_renovados(apps, schema_editor):
    Reporte = apps.get_model('dashboardgria', 'Reporte')
    Group = apps.get_model('auth', 'Group')

    defaults = {
        'nombre_visible': 'CDAT Cancelados No Renovados',
        'app_origen': 'comercial',
        'url_name': 'exportar_cdat_cancelados_excel',
        'descripcion': 'Descarga el listado de CDAT cancelados que no fueron renovados.',
        'icono_fa': 'fas fa-file-excel',
        'activo': True,
        'es_descarga': True,
        'card_template': 'gria/cards/filtro_agencias.html',
        'orden': 7,
        'tamaño': 1,
    }

    reporte, created = Reporte.objects.get_or_create(
        identificador='cdat-cancelados-no-renovados',
        defaults=defaults
    )

    if not created:
        updated = False
        for field, value in defaults.items():
            if getattr(reporte, field) != value:
                setattr(reporte, field, value)
                updated = True
        if updated:
            reporte.save()

    comercial_group, _ = Group.objects.get_or_create(name='comercial')
    reporte.grupos_permitidos.add(comercial_group)


def remove_cdat_cancelados_no_renovados(apps, schema_editor):
    Reporte = apps.get_model('dashboardgria', 'Reporte')
    Reporte.objects.filter(identificador='cdat-cancelados-no-renovados').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('dashboardgria', '0005_reporte_ahorros_programados_inactivos'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(
            create_cdat_cancelados_no_renovados,
            remove_cdat_cancelados_no_renovados
        ),
    ]
