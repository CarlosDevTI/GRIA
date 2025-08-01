# myapp/urls.py
from django.urls import path
from .views import (
    DashboardSarcView, DashboardSarcDataJsonView,
    # DashboardSarlView, DashboardSarlDataJsonView,
)

urlpatterns = [
    path('sarc/', DashboardSarcView.as_view(), name='dashboard_sarc'),
    path('sarc/data/', DashboardSarcDataJsonView.as_view(), name='dashboard_sarc_data_json'),
    # path('sarl/', DashboardSarlView.as_view(), name='dashboard_sarl'),
    # path('sarl/data/', DashboardSarlDataJsonView.as_view(), name='dashboard_sarl_data_json'),
]