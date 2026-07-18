from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from django.utils import timezone
from .models import Goal, BodyMeasurement, ProgressReport, Exercise, WorkoutPlan, DietPlan, TrainerAssignment
from .serializers import (
    GoalSerializer, BodyMeasurementSerializer, ProgressReportSerializer,
    ExerciseSerializer, WorkoutPlanSerializer, DietPlanSerializer, TrainerAssignmentSerializer
)
from apps.identity.permissions import IsTrainer, IsAdmin, IsAdminOrReceptionist, IsAssignedTrainerOrOwnerOrAdmin


class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.select_related('member').all()
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'member':
            return self.queryset.filter(member=user)
        if user.role == 'trainer':
            assigned_ids = TrainerAssignment.objects.filter(trainer=user, is_active=True).values_list('member_id', flat=True)
            return self.queryset.filter(member_id__in=assigned_ids)
        return self.queryset  # admin sees everyone

    def perform_create(self, serializer):
        serializer.save(member=self.request.user)


class BodyMeasurementViewSet(viewsets.ModelViewSet):
    """Members log their own measurements; trainers can log for assigned members too."""
    queryset = BodyMeasurement.objects.select_related('member', 'recorded_by').all()
    serializer_class = BodyMeasurementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'member':
            return self.queryset.filter(member=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        if self.request.user.role == 'member':
            serializer.save(member=self.request.user, recorded_by=self.request.user)
        else:
            # trainer/admin logging on behalf of a member — member id comes from the request body
            serializer.save(recorded_by=self.request.user)


class ProgressReportViewSet(viewsets.ModelViewSet):
    """Only trainers write progress reports; members can read their own."""
    queryset = ProgressReport.objects.select_related('member', 'trainer').all()
    serializer_class = ProgressReportSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsTrainer()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.role == 'member':
            return self.queryset.filter(member=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(trainer=self.request.user)


class ExerciseViewSet(viewsets.ModelViewSet):
    """The shared exercise library — admins and trainers manage it, everyone can read."""
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsTrainer()]  # trainers (and admins, if you add IsAdmin OR logic later) manage the library


class WorkoutPlanViewSet(viewsets.ModelViewSet):
    queryset = WorkoutPlan.objects.select_related('member', 'trainer').prefetch_related('exercises').all()
    serializer_class = WorkoutPlanSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsTrainer()]
        return [IsAuthenticated(), IsAssignedTrainerOrOwnerOrAdmin()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'member':
            return self.queryset.filter(member=user)
        if user.role == 'trainer':
            assigned_member_ids = TrainerAssignment.objects.filter(
                trainer=user, is_active=True
            ).values_list('member_id', flat=True)
            return self.queryset.filter(member_id__in=assigned_member_ids)
        return self.queryset

    def perform_create(self, serializer):
        member = serializer.validated_data['member']
        if self.request.user.role == 'trainer':
            is_assigned = TrainerAssignment.objects.filter(
                member=member, trainer=self.request.user, is_active=True
            ).exists()
            if not is_assigned:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You are not the assigned trainer for this member.")
        serializer.save(trainer=self.request.user)

class DietPlanViewSet(viewsets.ModelViewSet):
    """Same pattern as WorkoutPlan."""
    queryset = DietPlan.objects.select_related('member', 'trainer').prefetch_related('meals').all()
    serializer_class = DietPlanSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsTrainer()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.role == 'member':
            return self.queryset.filter(member=self.request.user)
        if self.request.user.role == 'trainer':
            return self.queryset.filter(trainer=self.request.user)
        return self.queryset
    
class TrainerAssignmentViewSet(viewsets.ModelViewSet):
    queryset = TrainerAssignment.objects.select_related('member', 'trainer').all()
    serializer_class = TrainerAssignmentSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminOrReceptionist()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'member':
            return self.queryset.filter(member=user)
        if user.role == 'trainer':
            return self.queryset.filter(trainer=user)
        return self.queryset  # admin/receptionist sees everyone

    def perform_create(self, serializer):
        member = serializer.validated_data['member']
        # Deactivate any existing active assignment for this member first
        TrainerAssignment.objects.filter(member=member, is_active=True).update(
            is_active=False, end_date=timezone.now().date()
        )
        serializer.save(assigned_by=self.request.user)