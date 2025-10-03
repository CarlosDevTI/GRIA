
#? NO VAMOS A TENER MODELOS POR EL MOMENTO 
#? YA QUE AL SER UN CONSULTA DIRECTA A ORACLE NO ES NECESARIO


# # MODELO FONDEOS
# from django.db import models
# from django.db import connection

# class RegistroFondeo(models.Model):
#     item = models.IntegerField()
#     agencia = models.CharField(max_length=100)
#     ahorra_facil = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     con_semilla = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     ahorra_junior = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     con_ahorrito = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     total_ahorros = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     cdat = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     contract = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     total_cdat_contractual = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     total_capt = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     aportes = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     cartera = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     capt_apo_cart = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     recuado_alcaldias = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     fecha_generacion = models.DateTimeField(auto_now_add=True)
#     fecha_corte_actual = models.DateField()
#     fecha_corte_anteior = models.DateField(null=True, blank=True)

#     class Meta:
#         db_table = 'fondeo'
#         verbose_name = 'Seguimiento de Fondeo'
#         verbose_name_plural = 'Seguimientos de Fondeo'
    
#     def __str__(self):
#         return f"{self.agencia} - {self.fecha_corte}"