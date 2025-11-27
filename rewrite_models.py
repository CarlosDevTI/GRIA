from pathlib import Path
path = Path('apps/riesgos/models.py')
text = '''from django.db import models

class ParametrosRiesgo(models.Model):
    """
    Almacena los parametros de riesgo y los valores de override para meses especificos
    que son cargados manualmente por el oficial de riesgos.
    """
    indicador_codigo = models.CharField(
        max_length=10,
        unique=True,
        primary_key=True,
        help_text="Codigo del indicador (ej. '1', '13', '2G') que coincide con el del SP de Oracle."
    )

    # Parametros de Apetito, Tolerancia y Capacidad
    apetito = models.FloatField(verbose_name="Apetito", null=True, blank=True)
    tolerancia = models.FloatField(verbose_name="Tolerancia", null=True, blank=True)
    capacidad = models.FloatField(verbose_name="Capacidad", null=True, blank=True)

    # Valor para sobrescribir el dato de un mes especifico
    valor_override = models.FloatField(verbose_name="Valor Manual", null=True, blank=True)
    valor_override_mes = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="Mes del Valor Manual",
        help_text="Mes para el valor de anulacion (formato MES-AA, ej. OCT-23). Si esta vacio, la anulacion no se aplica."
    )

    def __str__(self):
        return f"Parametros para el Indicador: {self.indicador_codigo}"

    class Meta:
        verbose_name = "Parametro de Riesgo"
        verbose_name_plural = "Parametros de Riesgo"
        ordering = ['indicador_codigo']


class ParametrosRiesgoSarL(models.Model):
    """
    Parametros de riesgo para SARL (separados de SARC para permitir valores independientes).
    """
    ASC = 'ASC'
    DESC = 'DESC'
    ORDEN_CHOICES = [
        (ASC, 'Ascendente'),
        (DESC, 'Descendente'),
    ]

    indicador_codigo = models.CharField(
        max_length=10,
        unique=True,
        primary_key=True,
        help_text="Codigo del indicador (ej. '1', '13', '2G') que coincide con el del SP de Oracle."
    )

    apetito = models.FloatField(verbose_name="Apetito", null=True, blank=True)
    tolerancia = models.FloatField(verbose_name="Tolerancia", null=True, blank=True)
    capacidad = models.FloatField(verbose_name="Capacidad", null=True, blank=True)

    valor_override = models.FloatField(verbose_name="Valor Manual", null=True, blank=True)
    valor_override_mes = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="Mes del Valor Manual",
        help_text="Mes para el valor de anulacion (formato MES-AA, ej. OCT-23). Si esta vacio, la anulacion no se aplica."
    )
    orden = models.CharField(
        max_length=4,
        choices=ORDEN_CHOICES,
        default=ASC,
        help_text="Define si el riesgo se calcula Ascendente o Descendente."
    )

    def __str__(self):
        return f"Parametros SARL para el Indicador: {self.indicador_codigo}"

    class Meta:
        verbose_name = "Parametro de Riesgo SARL"
        verbose_name_plural = "Parametros de Riesgo SARL"
        ordering = ['indicador_codigo']
'''
path.write_text(text, encoding='utf-8')
