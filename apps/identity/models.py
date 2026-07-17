from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model — every login (admin, receptionist, trainer, member)
    is a row here. Role-specific data lives in MemberProfile / StaffProfile,
    linked back to this User via a OneToOneField.
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        RECEPTIONIST = 'receptionist', 'Receptionist'
        TRAINER = 'trainer', 'Trainer'
        MEMBER = 'member', 'Member'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"