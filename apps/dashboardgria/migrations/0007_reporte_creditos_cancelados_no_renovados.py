from django.db import migrations


def create_creditos_cancelados_no_renovados(apps, schema_editor):
    Reporte = apps.get_model('dashboardgria', 'Reporte')
    Group = apps.get_model('auth', 'Group')

    defaults = {
        'nombre_visible': 'Créditos Cancelados No Renovados',
        'app_origen': 'comercial',
        'url_name': 'exportar_creditos_cancelados_excel',
        'descripcion': 'Descarga el listado de créditos cancelados que no fueron renovados.',
        'icono_fa': 'fas fa-file-excel',
        'activo': True,
        'es_descarga': True,
        'card_template': 'gria/cards/filtro_agencias.html',
        'orden': 8,
        'tamaño': 1,
    }

    reporte, created = Reporte.objects.get_or_create(
        identificador='creditos-cancelados-no-renovados',
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


def remove_creditos_cancelados_no_renovados(apps, schema_editor):
    Reporte = apps.get_model('dashboardgria', 'Reporte')
    Reporte.objects.filter(identificador='creditos-cancelados-no-renovados').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('dashboardgria', '0006_reporte_cdat_cancelados_no_renovados'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(
            create_creditos_cancelados_no_renovados,
            remove_creditos_cancelados_no_renovados
        ),
    ]
