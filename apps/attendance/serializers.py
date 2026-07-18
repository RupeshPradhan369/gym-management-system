from rest_framework import serializers
from .models import Attendance, StaffAttendance, QRToken


class AttendanceSerializer(serializers.ModelSerializer):
    member_username = serializers.CharField(source='member.username', read_only=True)
    marked_by_username = serializers.CharField(source='marked_by.username', read_only=True, default=None)

    class Meta:
        model = Attendance
        fields = [
            'id', 'member', 'member_username', 'check_in_time', 'check_out_time',
            'method', 'marked_by', 'marked_by_username',
        ]
        read_only_fields = ['id', 'check_in_time', 'method', 'marked_by']


class StaffAttendanceSerializer(serializers.ModelSerializer):
    staff_username = serializers.CharField(source='staff.username', read_only=True)

    class Meta:
        model = StaffAttendance
        fields = ['id', 'staff', 'staff_username', 'check_in_time', 'check_out_time']
        read_only_fields = ['id', 'check_in_time']


class QRTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRToken
        fields = ['id', 'member', 'token', 'created_at', 'expires_at', 'is_used']
        read_only_fields = ['id', 'member', 'token', 'created_at', 'is_used']