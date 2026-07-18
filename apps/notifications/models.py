from django.db import models

# Create your models here.
from django.db import models
from apps.identity.models import User


class Notification(models.Model):
    """
    A single notification for a user. Created by the backend itself
    (e.g. when a membership is renewed, or an admin posts an announcement) —
    not something a client POSTs directly in most cases.
    """

    class NotificationType(models.TextChoices):
        MEMBERSHIP_EXPIRY = 'membership_expiry', 'Membership Expiry'
        PAYMENT_SUCCESS = 'payment_success', 'Payment Success'
        ATTENDANCE_REMINDER = 'attendance_reminder', 'Attendance Reminder'
        ANNOUNCEMENT = 'announcement', 'Announcement'
        TRAINER_MESSAGE = 'trainer_message', 'Trainer Message'
        GENERAL = 'general', 'General'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices, default=NotificationType.GENERAL)
    title = models.CharField(max_length=150)
    body = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} → {self.user.username} ({'read' if self.is_read else 'unread'})"
    

class Announcement(models.Model):
    """
    Admin-created broadcast — e.g. 'Gym closed on Dashain', 'New yoga class'.
    Posting one automatically fans out a Notification to every active member
    (see the view, which calls notify() for each recipient).
    """

    class Audience(models.TextChoices):
        ALL_MEMBERS = 'all_members', 'All Members'
        ALL_STAFF = 'all_staff', 'All Staff'
        EVERYONE = 'everyone', 'Everyone'

    title = models.CharField(max_length=150)
    body = models.TextField()
    audience = models.CharField(max_length=20, choices=Audience.choices, default=Audience.ALL_MEMBERS)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='announcements_posted')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title