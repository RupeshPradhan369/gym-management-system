from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, MemberProfile, StaffProfile


class UserSerializer(serializers.ModelSerializer):
    """Read-only representation of a User — used nested inside profile responses."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number']
        read_only_fields = fields


class MemberProfileSerializer(serializers.ModelSerializer):
    """
    Handles both reading (nested user info) and writing (flat registration fields).
    This dual-purpose pattern is what the last session used successfully —
    read-only nested `user` for output, write-only flat fields for input.
    """
    user = UserSerializer(read_only=True)

    # Write-only fields, only used when creating a new member (registration)
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    phone_number = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = MemberProfile
        fields = [
            'id', 'user', 'member_code', 'date_of_birth', 'gender', 'address',
            'height_cm', 'weight_kg', 'profile_photo',
            'emergency_contact_name', 'emergency_contact_phone', 'created_at',
            # write-only registration fields:
            'username', 'email', 'password', 'first_name', 'last_name', 'phone_number',
        ]
        read_only_fields = ['id', 'member_code', 'created_at']

    def create(self, validated_data):
        # Pop the flat User fields out before creating MemberProfile
        user = User.objects.create_user(
            username=validated_data.pop('username'),
            email=validated_data.pop('email', ''),
            password=validated_data.pop('password'),
            first_name=validated_data.pop('first_name'),
            last_name=validated_data.pop('last_name', ''),
            phone_number=validated_data.pop('phone_number', ''),
            role=User.Role.MEMBER,
        )
        # Auto-generate a member_code, e.g. MEM-00007 based on the new user's id
        validated_data['member_code'] = f"MEM-{user.id:05d}"
        return MemberProfile.objects.create(user=user, **validated_data)


class StaffProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    role = serializers.ChoiceField(write_only=True, choices=['admin', 'receptionist', 'trainer'])

    class Meta:
        model = StaffProfile
        fields = [
            'id', 'user', 'employee_code', 'designation', 'hired_date', 'specialization',
            'username', 'email', 'password', 'first_name', 'last_name', 'role',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        role = validated_data.pop('role')
        user = User.objects.create_user(
            username=validated_data.pop('username'),
            email=validated_data.pop('email', ''),
            password=validated_data.pop('password'),
            first_name=validated_data.pop('first_name'),
            last_name=validated_data.pop('last_name', ''),
            role=role,
        )
        validated_data['employee_code'] = f"EMP-{user.id:05d}"
        return StaffProfile.objects.create(user=user, **validated_data)