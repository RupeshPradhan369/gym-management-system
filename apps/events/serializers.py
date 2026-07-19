from rest_framework import serializers
from .models import Event, EventRegistration


class EventRegistrationSerializer(serializers.ModelSerializer):
    member_username = serializers.CharField(source='member.username', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = EventRegistration
        fields = ['id', 'event', 'event_title', 'member', 'member_username', 'status', 'registered_at']
        read_only_fields = ['id', 'member', 'status', 'registered_at']


class EventSerializer(serializers.ModelSerializer):
    registration_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, default=None)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'event_date', 'start_time', 'location',
            'max_participants', 'registration_count', 'is_full',
            'created_by', 'created_by_username', 'created_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at']