from django.db import migrations


def create_creditos_retanqueo(apps, schema_editor):
    Reporte = apps.get_model('dashboardgria', 'Reporte')
    Group = apps.get_model('auth', 'Group')

    defaults = {
        'nombre_visible': 'Retanqueos',
        'app_origen': 'comercial',
        'url_name': 'exportar_creditos_retanqueo_excel',
        'descripcion': 'Descarga el listado de retanqueos por agencia.',
        'icono_fa': 'fas fa-redo',
        'activo': True,
        'es_descarga': True,
        'card_template': 'gria/cards/filtro_agencias.html',
        'orden': 9,
        'tamaño': 1,
    }

    reporte, created = Reporte.objects.get_or_create(
        identificador='creditos-retanqueo',
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


def remove_creditos_retanqueo(apps, schema_editor):
    Reporte = apps.get_model('dashboardgria', 'Reporte')
    Reporte.objects.filter(identificador='creditos-retanqueo').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('dashboardgria', '0007_reporte_creditos_cancelados_no_renovados'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(
            create_creditos_retanqueo,
            remove_creditos_retanqueo
        ),
    ]
