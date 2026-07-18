from django.urls import path
from .views import AdminSummaryView

urlpatterns = [
    path('dashboard/summary/', AdminSummaryView.as_view(), name='dashboard-summary'),
]