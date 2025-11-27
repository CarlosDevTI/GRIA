from django.db import migrations


def create_ahorros_programados_inactivos(apps, schema_editor):
    Reporte = apps.get_model('dashboardgria', 'Reporte')
    Group = apps.get_model('auth', 'Group')

    defaults = {
        'nombre_visible': 'Ahorros Programados',
        'app_origen': 'comercial',
        'url_name': 'exportar_ahorros_programados_excel',
        'descripcion': 'Descarga el listado de ahorros programados que requieren gestión.',
        'icono_fa': 'fas fa-piggy-bank',
        'activo': True,
        'es_descarga': True,
        'card_template': 'gria/cards/filtro_agencias.html',
        'orden': 6,
        'tamaño': 1,
    }

    reporte, created = Reporte.objects.get_or_create(
        identificador='ahorros-programados-inactivos',
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


def remove_ahorros_programados_inactivos(apps, schema_editor):
    Reporte = apps.get_model('dashboardgria', 'Reporte')
    Reporte.objects.filter(identificador='ahorros-programados-inactivos').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('dashboardgria', '0004_reporte_asociados_desactualizados'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(
            create_ahorros_programados_inactivos,
            remove_ahorros_programados_inactivos
        ),
    ]
