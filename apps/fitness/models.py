from django.db import models
from django.utils import timezone
from apps.identity.models import User


class Goal(models.Model):
    """A member's fitness goal — e.g. lose 5kg by a target date."""

    class GoalType(models.TextChoices):
        WEIGHT_LOSS = 'weight_loss', 'Weight Loss'
        MUSCLE_GAIN = 'muscle_gain', 'Muscle Gain'
        STRENGTH = 'strength', 'Strength'
        ENDURANCE = 'endurance', 'Endurance'
        GENERAL_FITNESS = 'general_fitness', 'General Fitness'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ACHIEVED = 'achieved', 'Achieved'
        ABANDONED = 'abandoned', 'Abandoned'

    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals', limit_choices_to={'role': 'member'})
    goal_type = models.CharField(max_length=20, choices=GoalType.choices)
    target_weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    target_body_fat_pct = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    start_date = models.DateField(default=timezone.localdate)
    target_date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.username} — {self.goal_type} by {self.target_date}"


class BodyMeasurement(models.Model):
    """A single measurement snapshot — the raw data points behind progress charts."""
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='measurements', limit_choices_to={'role': 'member'})
    recorded_date = models.DateField(default=timezone.localdate)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    body_fat_pct = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    chest_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    waist_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    arms_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    thigh_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='measurements_recorded')

    class Meta:
        ordering = ['-recorded_date']

    def __str__(self):
        return f"{self.member.username} @ {self.recorded_date}"


class ProgressReport(models.Model):
    """
    A trainer's periodic written review of a member's progress —
    distinct from raw measurements, this is qualitative feedback.
    """
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_reports', limit_choices_to={'role': 'member'})
    trainer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='progress_reports_written', limit_choices_to={'role': 'trainer'})
    report_date = models.DateField(default=timezone.localdate)
    summary = models.TextField()
    progress_photo = models.ImageField(upload_to='progress_photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Progress for {self.member.username} @ {self.report_date}"


class Exercise(models.Model):
    """The reusable exercise library — trainers build WorkoutPlans from these."""

    class Category(models.TextChoices):
        CARDIO = 'cardio', 'Cardio'
        STRENGTH = 'strength', 'Strength'
        FLEXIBILITY = 'flexibility', 'Flexibility'
        BALANCE = 'balance', 'Balance'

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.TextField(blank=True)
    demo_video_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class WorkoutPlan(models.Model):
    """A trainer-created workout plan assigned to a specific member."""
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_plans', limit_choices_to={'role': 'member'})
    trainer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='workout_plans_created', limit_choices_to={'role': 'trainer'})
    title = models.CharField(max_length=150)
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} for {self.member.username}"


class WorkoutExercise(models.Model):
    """A single exercise entry within a WorkoutPlan — e.g. 'Day 1: Squats, 4x10'."""
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT, related_name='workout_uses')
    day_number = models.PositiveIntegerField(help_text="e.g. 1 for Day 1, 2 for Day 2")
    sets = models.PositiveIntegerField(null=True, blank=True)
    reps = models.PositiveIntegerField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['day_number']

    def __str__(self):
        return f"{self.exercise.name} — Day {self.day_number}"


class DietPlan(models.Model):
    """A trainer-created diet plan assigned to a specific member."""
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diet_plans', limit_choices_to={'role': 'member'})
    trainer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='diet_plans_created', limit_choices_to={'role': 'trainer'})
    title = models.CharField(max_length=150)
    daily_calorie_target = models.PositiveIntegerField(null=True, blank=True)
    start_date = models.DateField(default=timezone.localdate)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} for {self.member.username}"


class Meal(models.Model):
    """A meal slot within a DietPlan — e.g. 'Breakfast', 'Lunch'."""

    class MealType(models.TextChoices):
        BREAKFAST = 'breakfast', 'Breakfast'
        LUNCH = 'lunch', 'Lunch'
        DINNER = 'dinner', 'Dinner'
        SNACK = 'snack', 'Snack'

    diet_plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE, related_name='meals')
    meal_type = models.CharField(max_length=10, choices=MealType.choices)
    description = models.TextField(help_text="e.g. '2 eggs, 1 toast, 1 banana'")
    calories = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.meal_type} — {self.diet_plan.title}"
    

class TrainerAssignment(models.Model):
    """
    Links a member to a trainer for personal training.
    Created when a member purchases a PT package (via billing).
    A member can have PT history with different trainers over time,
    but only ONE active assignment at a time.
    """
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trainer_assignments', limit_choices_to={'role': 'member'})
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_members', limit_choices_to={'role': 'trainer'})
    is_active = models.BooleanField(default=True)
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(null=True, blank=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='pt_assignments_made')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.member.username} → {self.trainer.username} ({'active' if self.is_active else 'ended'})"