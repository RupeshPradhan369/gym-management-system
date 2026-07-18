from rest_framework import serializers
from .models import MembershipPlan, Membership, MembershipFreeze


class MembershipPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipPlan
        fields = ['id', 'name', 'description', 'duration_value', 'duration_unit', 'price', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class MembershipFreezeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipFreeze
        fields = ['id', 'membership', 'freeze_start', 'freeze_end', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']


class MembershipSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    member_username = serializers.CharField(source='member.username', read_only=True)
    freezes = MembershipFreezeSerializer(many=True, read_only=True)

    class Meta:
        model = Membership
        fields = [
            'id', 'member', 'member_username', 'plan', 'plan_name',
            'start_date', 'end_date', 'status', 'freezes', 'created_at',
        ]
        # end_date is server-calculated — never accepted from the client
        read_only_fields = ['id', 'end_date', 'status', 'created_at']