from rest_framework import serializers
from .models import (
    Goal, BodyMeasurement, ProgressReport, Exercise,
    WorkoutPlan, WorkoutExercise, DietPlan, Meal, TrainerAssignment,
)


class GoalSerializer(serializers.ModelSerializer):
    member_username = serializers.CharField(source='member.username', read_only=True)

    class Meta:
        model = Goal
        fields = [
            'id', 'member', 'member_username', 'goal_type', 'target_weight_kg',
            'target_body_fat_pct', 'start_date', 'target_date', 'status', 'notes', 'created_at',
        ]
        read_only_fields = ['id', 'member', 'status', 'created_at']


class BodyMeasurementSerializer(serializers.ModelSerializer):
    member_username = serializers.CharField(source='member.username', read_only=True)
    recorded_by_username = serializers.CharField(source='recorded_by.username', read_only=True, default=None)

    class Meta:
        model = BodyMeasurement
        fields = [
            'id', 'member', 'member_username', 'recorded_date', 'weight_kg', 'body_fat_pct',
            'chest_cm', 'waist_cm', 'arms_cm', 'thigh_cm', 'recorded_by', 'recorded_by_username',
        ]
        read_only_fields = ['id', 'recorded_by']


class ProgressReportSerializer(serializers.ModelSerializer):
    member_username = serializers.CharField(source='member.username', read_only=True)
    trainer_username = serializers.CharField(source='trainer.username', read_only=True, default=None)

    class Meta:
        model = ProgressReport
        fields = [
            'id', 'member', 'member_username', 'trainer', 'trainer_username',
            'report_date', 'summary', 'progress_photo', 'created_at',
        ]
        read_only_fields = ['id', 'trainer', 'created_at']


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'category', 'description', 'demo_video_url', 'created_at']
        read_only_fields = ['id', 'created_at']


class WorkoutExerciseSerializer(serializers.ModelSerializer):
    exercise_name = serializers.CharField(source='exercise.name', read_only=True)

    class Meta:
        model = WorkoutExercise
        fields = ['id', 'exercise', 'exercise_name', 'day_number', 'sets', 'reps', 'duration_minutes', 'notes']
        read_only_fields = ['id']


class WorkoutPlanSerializer(serializers.ModelSerializer):
    exercises = WorkoutExerciseSerializer(many=True)
    member_username = serializers.CharField(source='member.username', read_only=True)
    trainer_username = serializers.CharField(source='trainer.username', read_only=True, default=None)

    class Meta:
        model = WorkoutPlan
        fields = [
            'id', 'member', 'member_username', 'trainer', 'trainer_username',
            'title', 'start_date', 'end_date', 'is_active', 'exercises', 'created_at',
        ]
        read_only_fields = ['id', 'trainer', 'created_at']

    def create(self, validated_data):
        exercises_data = validated_data.pop('exercises')
        request = self.context['request']
        plan = WorkoutPlan.objects.create(trainer=request.user, **validated_data)
        for ex_data in exercises_data:
            WorkoutExercise.objects.create(workout_plan=plan, **ex_data)
        return plan


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['id', 'meal_type', 'description', 'calories']
        read_only_fields = ['id']


class DietPlanSerializer(serializers.ModelSerializer):
    meals = MealSerializer(many=True)
    member_username = serializers.CharField(source='member.username', read_only=True)
    trainer_username = serializers.CharField(source='trainer.username', read_only=True, default=None)

    class Meta:
        model = DietPlan
        fields = [
            'id', 'member', 'member_username', 'trainer', 'trainer_username',
            'title', 'daily_calorie_target', 'start_date', 'is_active', 'meals', 'created_at',
        ]
        read_only_fields = ['id', 'trainer', 'created_at']

    def create(self, validated_data):
        meals_data = validated_data.pop('meals')
        request = self.context['request']
        plan = DietPlan.objects.create(trainer=request.user, **validated_data)
        for meal_data in meals_data:
            Meal.objects.create(diet_plan=plan, **meal_data)
        return plan
    

class TrainerAssignmentSerializer(serializers.ModelSerializer):
    member_username = serializers.CharField(source='member.username', read_only=True)
    trainer_username = serializers.CharField(source='trainer.username', read_only=True)

    class Meta:
        model = TrainerAssignment
        fields = ['id', 'member', 'member_username', 'trainer', 'trainer_username', 'is_active', 'start_date', 'end_date', 'created_at']
        read_only_fields = ['id', 'created_at']