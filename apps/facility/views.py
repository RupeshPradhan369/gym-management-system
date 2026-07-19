from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Equipment, Maintenance, Locker, LockerAssignment
from .serializers import EquipmentSerializer, MaintenanceSerializer, LockerSerializer, LockerAssignmentSerializer
from apps.identity.permissions import IsAdmin, IsAdminOrReceptionist


class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.prefetch_related('maintenance_records').all()
    serializer_class = EquipmentSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdmin()]


class MaintenanceViewSet(viewsets.ModelViewSet):
    queryset = Maintenance.objects.select_related('equipment', 'performed_by').all()
    serializer_class = MaintenanceSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)


class LockerViewSet(viewsets.ModelViewSet):
    queryset = Locker.objects.all()
    serializer_class = LockerSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdmin()]


class LockerAssignmentViewSet(viewsets.ModelViewSet):
    """
    POST /locker-assignments/            — assign a member to an available locker
    POST /locker-assignments/{id}/release/  — end the rental, free up the locker
    """
    queryset = LockerAssignment.objects.select_related('locker', 'member').all()
    serializer_class = LockerAssignmentSerializer

    def get_permissions(self):
        if self.action in ('create', 'release'):
            return [IsAdminOrReceptionist()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.role == 'member':
            return self.queryset.filter(member=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        locker = serializer.validated_data['locker']
        if locker.status != Locker.Status.AVAILABLE:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'locker': 'This locker is not available.'})

        assignment = serializer.save(assigned_by=self.request.user)
        locker.status = Locker.Status.OCCUPIED
        locker.save()

    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        assignment = self.get_object()
        if not assignment.is_active:
            return Response({'detail': 'This assignment is already ended.'}, status=400)

        assignment.is_active = False
        assignment.end_date = timezone.now().date()
        assignment.save()

        assignment.locker.status = Locker.Status.AVAILABLE
        assignment.locker.save()

        return Response(LockerAssignmentSerializer(assignment).data)