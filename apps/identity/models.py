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
    

class MemberProfile(models.Model):
    """
    Extra data for users with role=MEMBER.
    One-to-one with User: every member has exactly one profile,
    and every profile belongs to exactly one user.
    """

    class Gender(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'
        OTHER = 'other', 'Other'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='member_profile',
        limit_choices_to={'role': User.Role.MEMBER},
    )
    member_code = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, blank=True)
    address = models.CharField(max_length=255, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='member_photos/', null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.member_code})"


class StaffProfile(models.Model):
    """
    Extra data for users with role in (ADMIN, RECEPTIONIST, TRAINER).
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_profile',
    )
    employee_code = models.CharField(max_length=20, unique=True)
    designation = models.CharField(max_length=100, blank=True)
    hired_date = models.DateField(null=True, blank=True)
    specialization = models.CharField(max_length=255, blank=True)  # trainers: e.g. "Strength, Yoga"

    def __str__(self):
        return f"{self.user.username} ({self.employee_code})"