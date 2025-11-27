from django.db import migrations


def create_asociados_desactualizados(apps, schema_editor):
    Reporte = apps.get_model('dashboardgria', 'Reporte')
    Group = apps.get_model('auth', 'Group')

    defaults = {
        'nombre_visible': 'Asociados Desactualizados',
        'app_origen': 'comercial',
        'url_name': 'exportar_asociados_desactualizados_excel',
        'descripcion': 'Descarga el listado de asociados pendientes por actualización de datos.',
        'icono_fa': 'fas fa-user-clock',
        'activo': True,
        'es_descarga': True,
        'card_template': 'gria/cards/filtro_agencias.html',
        'orden': 5,
        'tamaño': 1,
    }

    reporte, created = Reporte.objects.get_or_create(
        identificador='asociados-desactualizados',
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


def remove_asociados_desactualizados(apps, schema_editor):
    Reporte = apps.get_model('dashboardgria', 'Reporte')
    Reporte.objects.filter(identificador='asociados-desactualizados').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('dashboardgria', '0003_reporte_orden_reporte_tamaño'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_asociados_desactualizados, remove_asociados_desactualizados),
    ]
