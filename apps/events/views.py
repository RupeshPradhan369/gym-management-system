from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Event, EventRegistration
from .serializers import EventSerializer, EventRegistrationSerializer
from apps.identity.permissions import IsAdminOrReceptionist


class EventViewSet(viewsets.ModelViewSet):
    """Everyone can view events; only admin/receptionist create/edit them."""
    queryset = Event.objects.select_related('created_by').prefetch_related('registrations').all()
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdminOrReceptionist()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        """POST /events/{id}/register/ — a member signs up for this event."""
        event = self.get_object()

        if event.is_full:
            return Response({'detail': 'This event is full.'}, status=400)

        existing = EventRegistration.objects.filter(event=event, member=request.user).first()
        if existing:
            if existing.status == EventRegistration.Status.CANCELLED:
                # they cancelled before — let them re-register instead of blocking forever
                existing.status = EventRegistration.Status.REGISTERED
                existing.save()
                return Response(EventRegistrationSerializer(existing).data)
            return Response({'detail': 'You are already registered for this event.'}, status=400)

        registration = EventRegistration.objects.create(event=event, member=request.user)
        return Response(EventRegistrationSerializer(registration).data, status=201)

    @action(detail=True, methods=['post'])
    def cancel_registration(self, request, pk=None):
        """POST /events/{id}/cancel_registration/ — member cancels their own registration."""
        event = self.get_object()
        try:
            registration = EventRegistration.objects.get(event=event, member=request.user)
        except EventRegistration.DoesNotExist:
            return Response({'detail': 'You are not registered for this event.'}, status=400)

        registration.status = EventRegistration.Status.CANCELLED
        registration.save()
        return Response(EventRegistrationSerializer(registration).data)


class EventRegistrationViewSet(viewsets.ReadOnlyModelViewSet):
    """View registrations — members see only their own; staff see all."""
    queryset = EventRegistration.objects.select_related('event', 'member').all()
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'member':
            return self.queryset.filter(member=self.request.user)
        return self.queryset