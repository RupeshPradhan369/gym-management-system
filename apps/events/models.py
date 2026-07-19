from django.db import models
from django.utils import timezone
from apps.identity.models import User


class Event(models.Model):
    """A gym-hosted event — bodybuilding competition, yoga session, seminar."""

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    event_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    max_participants = models.PositiveIntegerField(null=True, blank=True, help_text="Leave blank for unlimited")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='events_created')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['event_date']

    @property
    def registration_count(self):
        return self.registrations.filter(status=EventRegistration.Status.REGISTERED).count()

    @property
    def is_full(self):
        if self.max_participants is None:
            return False
        return self.registration_count >= self.max_participants

    def __str__(self):
        return f"{self.title} ({self.event_date})"


class EventRegistration(models.Model):
    """A member's registration for an Event."""

    class Status(models.TextChoices):
        REGISTERED = 'registered', 'Registered'
        CANCELLED = 'cancelled', 'Cancelled'
        ATTENDED = 'attended', 'Attended'

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations', limit_choices_to={'role': 'member'})
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.REGISTERED)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'member')  # a member can only register once per event

    def __str__(self):
        return f"{self.member.username} → {self.event.title} ({self.status})"