from django.urls import path
from . import views

urlpatterns = [
    #* ----- FONDEOS ----------
    path('seguimiento-fondeo/', views.seguimiento_fondeo, name='seguimiento_fondeo'),
    path('exportar-fondeo-excel/', views.exportar_fondeo_excel, name='exportar_fondeo_excel'),
    #* ----- ASOCIADOS SIN PRODUCTOS --------
    path('asociados-sin-productos/', views.asociados_sin_productos_view, name='asociados_sin_productos'),
    path('exportar-asociados-sin-productos-excel/', views.exportar_asociados_sin_productos_excel, name='exportar_asociados_sp'),
    #* ----- APORTES -----------
    path('aportes/', views.detalles_aportes, name='aportes'),
    path('exportar-aportes-excel/', views.exportar_excel_aportes, name='exportar_aportes_excel'),
    path('detalle-aportes/', views.detalles_aportes, name='detalle_aportes'),
    path('resumen-aportes-ai/', views.generar_resumen_aportes, name='generar_resumen_aportes_ai'), # Vista de Resumen de IA
    path('generar-recaudo-aportes-detalle/', views.generar_recaudo_aportes_detalle, name='generar_recaudo_aportes_detalle'), # Vista de Detalle de Recaudo de aportes por cédula
    #* ----- FINALIZACION DE APORTES -----------
]