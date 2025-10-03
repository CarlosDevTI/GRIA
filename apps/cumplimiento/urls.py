from django.urls import path
from . import views

urlpatterns = [
    path('sarlaft/', views.lista_indicadores, name='lista_indicadores'),
    path('agregar/', views.agregar_indicador, name='agregar_indicador'),
    path('editar/<int:id>/', views.editar_indicador, name='editar_indicador'),
    path('eliminar/<int:id>/', views.eliminar_indicador, name='eliminar_indicador'),
    
    #* URLs para manejar múltiples fórmulas
    path('indicador/<int:indicador_id>/agregar-formula/', views.agregar_formula, name='agregar_formula'),
    path('formula/editar/<int:formula_id>/', views.editar_formula, name='editar_formula'),
    path('formula/eliminar/<int:formula_id>/', views.eliminar_formula, name='eliminar_formula'),
    
    #* URLs para registros (ahora asociados a fórmulas específicas)
    path('formula/<int:formula_id>/registros/', views.gestionar_registros, name='gestionar_registros'),
    path('registros/editar/<int:id>/', views.editar_registro, name='editar_registro'),
    path('registros/eliminar/<int:id>/', views.eliminar_registro, name='eliminar_registro'),
    
    path('importar/', views.importar_indicadores, name='importar_indicadores'),
    path('importar-registros/', views.importar_registros, name='importar_registros'),

    #? - URLS PARA DESCARGAR PLANTILLAS -
    path('descargar-plantilla-indicadores/', views.descargar_plantilla_indicadores, name='descargar_plantilla_indicadores'),
    path('descargar-plantilla-registros/', views.descargar_plantilla_registros, name='descargar_plantilla_registros'),

    #? - URLS CALIDAD - DATA -
    path('calidad-data/', views.exp_excel_cumplimiento_data, name='calidad_data'),
]