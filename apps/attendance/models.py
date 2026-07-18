import uuid
from django.db import models
from django.utils import timezone
from apps.identity.models import User


class Attendance(models.Model):
    """
    One row per check-in. check_out_time is nullable — filled in later
    (or never, if the gym doesn't track checkout, which is common).
    """

    class Method(models.TextChoices):
        QR = 'qr', 'QR Scan'
        MANUAL = 'manual', 'Manual Entry'

    member = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='attendances',
        limit_choices_to={'role': 'member'},
    )
    check_in_time = models.DateTimeField(default=timezone.now)
    check_out_time = models.DateTimeField(null=True, blank=True)
    method = models.CharField(max_length=10, choices=Method.choices, default=Method.QR)
    marked_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='attendances_marked',
        help_text="Staff who recorded this — null for self check-in via QR.",
    )

    class Meta:
        ordering = ['-check_in_time']

    def __str__(self):
        return f"{self.member.username} @ {self.check_in_time:%Y-%m-%d %H:%M}"


class StaffAttendance(models.Model):
    """Separate table for staff (trainer/receptionist) attendance — different reporting needs than members."""
    staff = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='staff_attendances',
    )
    check_in_time = models.DateTimeField(default=timezone.now)
    check_out_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-check_in_time']

    def __str__(self):
        return f"{self.staff.username} @ {self.check_in_time:%Y-%m-%d %H:%M}"


class QRToken(models.Model):
    """
    A short-lived, single-use token shown as a QR code in the member's app.
    The gym's scanner app posts this token to /attendance/check-in/ — the
    backend validates it hasn't expired or been used before creating an
    Attendance row.
    """
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='qr_tokens', limit_choices_to={'role': 'member'})
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def __str__(self):
        return f"QR for {self.member.username} ({'used' if self.is_used else 'active'})"