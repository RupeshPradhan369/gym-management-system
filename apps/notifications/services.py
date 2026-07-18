from .models import Notification


def notify(user, title, body='', notification_type=Notification.NotificationType.GENERAL):
    """
    Central helper — call this from any app to create a notification.
    Usage: from apps.notifications.services import notify
           notify(membership.member, "Payment received", "Your payment of...", Notification.NotificationType.PAYMENT_SUCCESS)
    """
    return Notification.objects.create(
        user=user,
        title=title,
        body=body,
        notification_type=notification_type,
    )