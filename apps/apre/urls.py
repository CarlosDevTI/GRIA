from django.urls import path
from . import views

app_name = 'apre'

urlpatterns = [
    path('', views.apre_report_view, name='apre_home'),
    path('download-excel/', views.download_apre_excel, name='download_excel'),
    path('generate-summary/', views.generate_summary_view, name='generate_summary'),
]