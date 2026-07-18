from django.contrib import admin
from .models import (
    Goal, BodyMeasurement, ProgressReport, Exercise,
    WorkoutPlan, WorkoutExercise, DietPlan, Meal,
)


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('member', 'goal_type', 'target_date', 'status')
    list_filter = ('goal_type', 'status')


@admin.register(BodyMeasurement)
class BodyMeasurementAdmin(admin.ModelAdmin):
    list_display = ('member', 'recorded_date', 'weight_kg', 'body_fat_pct')
    search_fields = ('member__username',)


@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    list_display = ('member', 'trainer', 'report_date')
    search_fields = ('member__username',)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)


class WorkoutExerciseInline(admin.TabularInline):
    model = WorkoutExercise
    extra = 1


@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'member', 'trainer', 'is_active')
    list_filter = ('is_active',)
    inlines = [WorkoutExerciseInline]


class MealInline(admin.TabularInline):
    model = Meal
    extra = 1


@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'member', 'trainer', 'is_active')
    list_filter = ('is_active',)
    inlines = [MealInline]