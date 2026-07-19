from rest_framework import viewsets

from .models import AuditLog, AppSetting
from .serializers import AuditLogSerializer, AppSettingSerializer
from apps.identity.permissions import IsAdmin


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Admin-only, read-only — you can view history but never edit/delete it via API."""
    queryset = AuditLog.objects.select_related('user').all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin]


class AppSettingViewSet(viewsets.ModelViewSet):
    """Admin manages gym-wide settings."""
    queryset = AppSetting.objects.all()
    serializer_class = AppSettingSerializer
    permission_classes = [IsAdmin]