from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Notification, Announcement
from .serializers import NotificationSerializer, AnnouncementSerializer
from .services import notify
from apps.identity.models import User
from apps.identity.permissions import IsAdmin


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    # ... (unchanged from before) ...
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        updated_count = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'marked_read': updated_count})


class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    GET  /announcements/   — everyone can read
    POST /announcements/   — admin only; automatically notifies the target audience
    """
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdmin()]

    def perform_create(self, serializer):
        announcement = serializer.save(posted_by=self.request.user)

        if announcement.audience == Announcement.Audience.ALL_MEMBERS:
            recipients = User.objects.filter(role=User.Role.MEMBER)
        elif announcement.audience == Announcement.Audience.ALL_STAFF:
            recipients = User.objects.filter(role__in=['admin', 'receptionist', 'trainer'])
        else:  # everyone
            recipients = User.objects.all()

        for user in recipients:
            notify(
                user=user,
                title=announcement.title,
                body=announcement.body,
                notification_type=Notification.NotificationType.ANNOUNCEMENT,
            )