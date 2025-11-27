from django.db import migrations


def create_saldos_asociados(apps, schema_editor):
    Reporte = apps.get_model('dashboardgria', 'Reporte')
    Group = apps.get_model('auth', 'Group')

    defaults = {
        'nombre_visible': 'Saldos Asociados',
        'app_origen': 'comercial',
        'url_name': 'exportar_saldos_asociados_excel',
        'descripcion': 'Descarga el informe de saldos de asociados.',
        'icono_fa': 'fas fa-balance-scale',
        'activo': True,
        'es_descarga': True,
        'card_template': 'gria/cards/filtro_agencias.html',
        'orden': 10,
        'tamaño': 1,
    }

    reporte, created = Reporte.objects.get_or_create(
        identificador='saldos-asociados',
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


def remove_saldos_asociados(apps, schema_editor):
    Reporte = apps.get_model('dashboardgria', 'Reporte')
    Reporte.objects.filter(identificador='saldos-asociados').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('dashboardgria', '0008_reporte_creditos_retanqueo'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(
            create_saldos_asociados,
            remove_saldos_asociados
        ),
    ]
