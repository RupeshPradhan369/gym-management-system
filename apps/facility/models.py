from django.db import models
from django.utils import timezone
from apps.identity.models import User


class Equipment(models.Model):
    """Gym equipment inventory — treadmills, weights, machines."""

    class Category(models.TextChoices):
        CARDIO = 'cardio', 'Cardio'
        STRENGTH = 'strength', 'Strength'
        FREE_WEIGHTS = 'free_weights', 'Free Weights'
        OTHER = 'other', 'Other'

    class Status(models.TextChoices):
        OPERATIONAL = 'operational', 'Operational'
        UNDER_MAINTENANCE = 'under_maintenance', 'Under Maintenance'
        OUT_OF_SERVICE = 'out_of_service', 'Out of Service'

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=Category.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPERATIONAL)
    purchase_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.status})"


class Maintenance(models.Model):
    """A maintenance event/record for a piece of equipment."""
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_records')
    description = models.TextField()
    performed_date = models.DateField(default=timezone.localdate)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='maintenance_logged')

    class Meta:
        ordering = ['-performed_date']

    def __str__(self):
        return f"Maintenance on {self.equipment.name} @ {self.performed_date}"


class Locker(models.Model):
    """A physical locker unit available for rent."""

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        OCCUPIED = 'occupied', 'Occupied'
        OUT_OF_SERVICE = 'out_of_service', 'Out of Service'

    locker_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    monthly_fee = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Locker {self.locker_number} ({self.status})"


class LockerAssignment(models.Model):
    """A member's rental period for a specific locker."""
    locker = models.ForeignKey(Locker, on_delete=models.CASCADE, related_name='assignments')
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locker_assignments', limit_choices_to={'role': 'member'})
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='locker_assignments_made')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Locker {self.locker.locker_number} → {self.member.username}"