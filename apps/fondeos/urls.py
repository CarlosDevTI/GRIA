from django.urls import path
from . import views

urlpatterns = [
    path('Seguimiento-fondeo/', views.seguimiento_fondeo, name='seguimiento_fondeo'),
    path('exportar-fondeo-excel/', views.exportar_fondeo_excel, name='exportar_fondeo_excel'),

]