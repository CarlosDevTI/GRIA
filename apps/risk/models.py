from django.db import models

class ParametrosRiesgo(models.Model):
    """
    Almacena los parámetros de riesgo y los valores de override para el último mes
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

    # Valor para sobrescribir el dato del último mes
    valor_override = models.FloatField(verbose_name="Valor Manual (último mes)", null=True, blank=True)

    def __str__(self):
        return f"Parámetros para el Indicador: {self.indicador_codigo}"

    class Meta:
        verbose_name = "Parámetro de Riesgo"
        verbose_name_plural = "Parámetros de Riesgo"
        ordering = ['indicador_codigo']
