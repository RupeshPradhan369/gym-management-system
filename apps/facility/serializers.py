from rest_framework import serializers
from .models import Equipment, Maintenance, Locker, LockerAssignment


class MaintenanceSerializer(serializers.ModelSerializer):
    performed_by_username = serializers.CharField(source='performed_by.username', read_only=True, default=None)

    class Meta:
        model = Maintenance
        fields = ['id', 'equipment', 'description', 'performed_date', 'cost', 'performed_by', 'performed_by_username']
        read_only_fields = ['id', 'performed_by']


class EquipmentSerializer(serializers.ModelSerializer):
    maintenance_records = MaintenanceSerializer(many=True, read_only=True)

    class Meta:
        model = Equipment
        fields = ['id', 'name', 'category', 'status', 'purchase_date', 'notes', 'maintenance_records', 'created_at']
        read_only_fields = ['id', 'created_at']


class LockerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locker
        fields = ['id', 'locker_number', 'status', 'monthly_fee']
        read_only_fields = ['id', 'status']  # status is only ever changed via assignment actions, not directly


class LockerAssignmentSerializer(serializers.ModelSerializer):
    member_username = serializers.CharField(source='member.username', read_only=True)
    locker_number = serializers.CharField(source='locker.locker_number', read_only=True)

    class Meta:
        model = LockerAssignment
        fields = [
            'id', 'locker', 'locker_number', 'member', 'member_username',
            'start_date', 'end_date', 'is_active', 'assigned_by', 'created_at',
        ]
        read_only_fields = ['id', 'end_date', 'is_active', 'assigned_by', 'created_at']