from rest_framework import serializers
from .models import AuditLog, AppSetting


class AuditLogSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True, default=None)

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'user_username', 'action', 'model_name', 'object_id', 'object_repr', 'changes', 'created_at']
        read_only_fields = fields  # entirely read-only — never created via API directly


class AppSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppSetting
        fields = ['id', 'key', 'value', 'description', 'updated_at']
        read_only_fields = ['id', 'updated_at']