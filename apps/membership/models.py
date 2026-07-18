from django.db import models
from apps.identity.models import User


class MembershipPlan(models.Model):
    """The catalog of plans a gym offers — e.g. Monthly, Quarterly, Yearly."""

    class DurationUnit(models.TextChoices):
        DAYS = 'days', 'Days'
        MONTHS = 'months', 'Months'

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration_value = models.PositiveIntegerField(help_text="e.g. 1, 3, 12")
    duration_unit = models.CharField(max_length=10, choices=DurationUnit.choices, default=DurationUnit.MONTHS)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.duration_value} {self.duration_unit})"


class Membership(models.Model):
    """
    A specific member's subscription to a plan.
    end_date is ALWAYS computed server-side from start_date + plan duration —
    never accepted directly from the client. This is the exact bug the
    previous session hit and fixed.
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        FROZEN = 'frozen', 'Frozen'
        EXPIRED = 'expired', 'Expired'
        CANCELLED = 'cancelled', 'Cancelled'

    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships', limit_choices_to={'role': 'member'})
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT, related_name='memberships')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.username} — {self.plan.name} ({self.status})"


class MembershipFreeze(models.Model):
    """
    Tracks pause periods on a membership. When a membership is frozen,
    its end_date gets pushed out by the freeze duration once resumed.
    """
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='freezes')
    freeze_start = models.DateField()
    freeze_end = models.DateField(null=True, blank=True)  # null while still frozen
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Freeze for {self.membership} from {self.freeze_start}"