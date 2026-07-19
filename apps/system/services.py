from .models import AuditLog


def log_action(user, action, instance, changes=None):
    """
    Central helper — call this from any view after create/update/delete.
    Usage: log_action(request.user, AuditLog.Action.UPDATE, membership, changes={'status': ['active', 'frozen']})
    """
    return AuditLog.objects.create(
        user=user,
        action=action,
        model_name=instance.__class__.__name__,
        object_id=str(instance.pk),
        object_repr=str(instance)[:255],
        changes=changes,
    )


def get_setting(key, default=None):
    """
    Fetch an AppSetting value by key. Returns `default` if not found.
    Note: value is always a string (TextField) — caller is responsible
    for casting to int/bool/etc. as needed.
    """
    from .models import AppSetting
    try:
        return AppSetting.objects.get(key=key).value
    except AppSetting.DoesNotExist:
        return default