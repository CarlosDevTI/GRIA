from django.db import models
from django.contrib.auth.models import Group

#? CENTRALIZAMOS ESTE MODELO COMO EL MODELO PRINCIPAL
#? UNICAMENTE LOS QUE VAMOS A BUSCAR ES:
#? VALIDAR QUE SI USEN GRIA, Y CUAL ES EL REPORTE 
#? MAS GENERADO PARA LLEVAR EL CONTROL


class ReporteMasUsado(models.Model):
    nombre_informe = models.CharField(max_length=255)
    usuario = models.CharField(max_length=150)
    fecha_ejecucion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reporte_mas_usado'
        verbose_name = 'Reporte Más Usado'
        verbose_name_plural = 'Reportes Más Usados'

    def __str__(self):
        return f"{self.nombre_informe} - {self.usuario} - {self.fecha_ejecucion}"

# --- NUEVO MODELO PARA GESTIÓN DE PERMISOS Y VISUALIZACIÓN ---

class Reporte(models.Model):
    """
    Representa un reporte o item individual que se mostrará en el dashboard principal.
    """
    nombre_visible = models.CharField(max_length=100, unique=True, help_text="Nombre del reporte que se mostrará en el dashboard.")
    identificador = models.SlugField(max_length=100, unique=True, help_text="Identificador único para el reporte (sin espacios ni caracteres especiales).")
    app_origen = models.CharField(max_length=50, help_text="Nombre de la app Django a la que pertenece el reporte.")
    url_name = models.CharField(max_length=100, help_text="Nombre de la URL (definida en urls.py) para acceder al reporte.")
    grupos_permitidos = models.ManyToManyField(
        Group,
        blank=True,
        help_text="Selecciona los grupos que tendrán acceso a este reporte."
    )
    
    # --- CAMPOS PARA UN TEMPLATE 100% DINÁMICO ---
    descripcion = models.TextField(max_length=250, help_text="Descripción que aparecerá en la tarjeta del dashboard.")
    icono_fa = models.CharField(max_length=50, help_text="Clase del icono de Font Awesome (ej: 'fas fa-chart-line').")
    activo = models.BooleanField(default=True, help_text="Si no está activo, se mostrará como 'Próximamente'.")
    es_descarga = models.BooleanField(default=False, help_text="Marcar si este reporte es una descarga de archivo en lugar de una página de dashboard.")
    card_template = models.CharField(max_length=200, blank=True, null=True, help_text="Ruta a la plantilla de la tarjeta para este reporte (ej: 'gria/cards/_fondeos.html').")


    def __str__(self):
        return self.nombre_visible

    class Meta:
        verbose_name = "Reporte del Dashboard"
        verbose_name_plural = "Reportes del Dashboard"
