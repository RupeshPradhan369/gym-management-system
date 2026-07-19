from rest_framework.routers import DefaultRouter
from .views import EquipmentViewSet, MaintenanceViewSet, LockerViewSet, LockerAssignmentViewSet

router = DefaultRouter()
router.register(r'equipment', EquipmentViewSet, basename='equipment')
router.register(r'maintenance', MaintenanceViewSet, basename='maintenance')
router.register(r'lockers', LockerViewSet, basename='locker')
router.register(r'locker-assignments', LockerAssignmentViewSet, basename='locker-assignment')

urlpatterns = router.urls