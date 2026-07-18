from rest_framework import serializers
from .models import Notification, Announcement


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'body', 'is_read', 'created_at']
        read_only_fields = ['id', 'notification_type', 'title', 'body', 'created_at']


class AnnouncementSerializer(serializers.ModelSerializer):
    posted_by_username = serializers.CharField(source='posted_by.username', read_only=True, default=None)

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'body', 'audience', 'posted_by', 'posted_by_username', 'created_at']
        read_only_fields = ['id', 'posted_by', 'created_at']