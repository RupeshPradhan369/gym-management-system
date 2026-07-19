from django.db import models
from apps.identity.models import User


class AuditLog(models.Model):
    """
    Records who did what to which record. Written automatically by a
    shared helper (log_action, added next) — never created directly
    by client requests.
    """

    class Action(models.TextChoices):
        CREATE = 'create', 'Create'
        UPDATE = 'update', 'Update'
        DELETE = 'delete', 'Delete'

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=10, choices=Action.choices)
    model_name = models.CharField(max_length=100, help_text="e.g. 'Membership', 'Invoice'")
    object_id = models.CharField(max_length=50)
    object_repr = models.CharField(max_length=255, blank=True, help_text="Human-readable snapshot, e.g. str(instance) at the time")
    changes = models.JSONField(null=True, blank=True, help_text="Old/new values for updates")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} {self.action} {self.model_name}#{self.object_id}"


class AppSetting(models.Model):
    """
    Simple key-value store for gym-wide configurable settings —
    e.g. QR token validity duration, default currency, gym name.
    Avoids hardcoding these as Python constants scattered across apps.
    """
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key} = {self.value}"