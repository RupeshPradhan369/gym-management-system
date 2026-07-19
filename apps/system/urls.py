from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet, AppSettingViewSet

router = DefaultRouter()
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'settings', AppSettingViewSet, basename='app-setting')

urlpatterns = router.urls