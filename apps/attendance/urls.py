from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    GenerateQRView, CheckInView, ManualCheckInView,
    AttendanceViewSet, StaffAttendanceViewSet,
)

router = DefaultRouter()
router.register(r'attendance-records', AttendanceViewSet, basename='attendance')
router.register(r'staff-attendance', StaffAttendanceViewSet, basename='staff-attendance')

urlpatterns = [
    path('attendance/qr/generate/', GenerateQRView.as_view(), name='qr-generate'),
    path('attendance/check-in/', CheckInView.as_view(), name='check-in'),
    path('attendance/manual-check-in/', ManualCheckInView.as_view(), name='manual-check-in'),
] + router.urls