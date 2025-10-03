from django.db import models

class Indicador(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    orden = models.IntegerField(default=0)
    
    def __str__(self):
        return self.nombre

class Formula(models.Model):
    FRECUENCIA_CHOICES = [
        ('Mensual', 'Mensual'),
        ('Trimestral', 'Trimestral'),
        ('Semestral', 'Semestral'),
        ('Anual', 'Anual'),
    ]

    indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, related_name='formulas')
    descripcion = models.TextField()
    meta = models.CharField(max_length=100)
    frecuencia_medicion = models.CharField(max_length=20, choices=FRECUENCIA_CHOICES)

    def __str__(self):
        return f"{self.indicador.nombre} - {self.descripcion[:50]}"

class RegistroIndicador(models.Model):
    MESES = [
        ('Enero', 'Enero'),
        ('Febrero', 'Febrero'),
        ('Marzo', 'Marzo'),
        ('Abril', 'Abril'),
        ('Mayo', 'Mayo'),
        ('Junio', 'Junio'),
        ('Julio', 'Julio'),
        ('Agosto', 'Agosto'),
        ('Septiembre', 'Septiembre'),
        ('Octubre', 'Octubre'),
        ('Noviembre', 'Noviembre'),
        ('Diciembre', 'Diciembre'),
    ]
    
    formula = models.ForeignKey(Formula, on_delete=models.CASCADE, related_name='registros')
    mes = models.CharField(max_length=20, choices=MESES)
    año = models.PositiveIntegerField()  # Corregido
    valor = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('formula', 'mes', 'año')  # Corregido
        ordering = ['año', 'mes']  # Corregido
    
    def __str__(self):
        return f"{self.formula.indicador.nombre} - {self.mes} {self.año}"  # Corregido