from django.db import models

class ParametrosRiesgo(models.Model):
    """
    Almacena los parámetros de riesgo y los valores de override para meses específicos
    que son cargados manualmente por el oficial de riesgos.
    """
    indicador_codigo = models.CharField(
        max_length=10, 
        unique=True, 
        primary_key=True, 
        help_text="Código del indicador (ej. '1', '13', '2G') que coincide con el del SP de Oracle."
    )

    # Parámetros de Apetito, Tolerancia y Capacidad
    apetito = models.FloatField(verbose_name="Apetito", null=True, blank=True)
    tolerancia = models.FloatField(verbose_name="Tolerancia", null=True, blank=True)
    capacidad = models.FloatField(verbose_name="Capacidad", null=True, blank=True)

    # Valor para sobrescribir el dato de un mes específico
    valor_override = models.FloatField(verbose_name="Valor Manual", null=True, blank=True)
    valor_override_mes = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="Mes del Valor Manual",
        help_text="Mes para el valor de anulación (formato MES-AA, ej. OCT-23). Si está vacío, la anulación no se aplica."
    )

    def __str__(self):
        return f"Parámetros para el Indicador: {self.indicador_codigo}"

    class Meta:
        verbose_name = "Parámetro de Riesgo"
        verbose_name_plural = "Parámetros de Riesgo"
        ordering = ['indicador_codigo']
