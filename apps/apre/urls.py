from django.urls import path
from . import views

urlpatterns = [
    path('', views.apre_report_view, name='apre_home'),
    path('download-excel/', views.download_apre_excel, name='download_excel'),
    path('generate-summary/', views.generate_summary_view, name='generate_summary'),
]