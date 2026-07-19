from django.contrib import admin
from .models import AuditLog, AppSetting


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'action', 'model_name', 'object_id')
    list_filter = ('action', 'model_name')
    search_fields = ('object_repr', 'user__username')
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'object_repr', 'changes', 'created_at')

    def has_add_permission(self, request):
        return False  # audit logs are system-generated only, never manually created


@admin.register(AppSetting)
class AppSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'updated_at')
    search_fields = ('key',)