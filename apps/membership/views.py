from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import MembershipPlan, Membership, MembershipFreeze
from .serializers import MembershipPlanSerializer, MembershipSerializer, MembershipFreezeSerializer
from apps.identity.permissions import IsAdmin, IsAdminOrReceptionist


class MembershipPlanViewSet(viewsets.ModelViewSet):
    queryset = MembershipPlan.objects.all()
    serializer_class = MembershipPlanSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdmin()]  # only admin creates/edits/deletes plans


class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.select_related('member', 'plan').prefetch_related('freezes').all()
    serializer_class = MembershipSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminOrReceptionist()]
        return [IsAuthenticated()]

    def get_queryset(self):
        # members only see their own memberships; staff see everyone
        qs = self.queryset
        if self.request.user.role == 'member':
            return qs.filter(member=self.request.user)
        return qs

    def perform_create(self, serializer):
        """
        This is the fix from last session: end_date is NEVER trusted from
        the client. We compute it here from start_date + the plan's duration.
        """
        plan = serializer.validated_data['plan']
        start_date = serializer.validated_data.get('start_date', timezone.now().date())

        if plan.duration_unit == MembershipPlan.DurationUnit.MONTHS:
            end_date = start_date + relativedelta(months=plan.duration_value)
        else:  # days
            end_date = start_date + timedelta(days=plan.duration_value)

        serializer.save(end_date=end_date, status=Membership.Status.ACTIVE)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrReceptionist])
    def freeze(self, request, pk=None):
        """POST /memberships/{id}/freeze/  body: {"reason": "..."}"""
        membership = self.get_object()
        if membership.status != Membership.Status.ACTIVE:
            return Response({'detail': 'Only active memberships can be frozen.'}, status=400)

        MembershipFreeze.objects.create(
            membership=membership,
            freeze_start=timezone.now().date(),
            reason=request.data.get('reason', ''),
        )
        membership.status = Membership.Status.FROZEN
        membership.save()

        # Re-fetch to avoid the stale prefetch-cache bug from last session
        membership.refresh_from_db()
        return Response(MembershipSerializer(membership).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrReceptionist])
    def unfreeze(self, request, pk=None):
        """POST /memberships/{id}/unfreeze/ — closes the open freeze, extends end_date by frozen duration."""
        membership = self.get_object()
        open_freeze = membership.freezes.filter(freeze_end__isnull=True).order_by('-freeze_start').first()
        if not open_freeze:
            return Response({'detail': 'No active freeze found.'}, status=400)

        today = timezone.now().date()
        open_freeze.freeze_end = today
        open_freeze.save()

        frozen_days = (today - open_freeze.freeze_start).days
        membership.end_date = membership.end_date + timedelta(days=frozen_days)
        membership.status = Membership.Status.ACTIVE
        membership.save()

        membership.refresh_from_db()
        return Response(MembershipSerializer(membership).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrReceptionist])
    def renew(self, request, pk=None):
        """POST /memberships/{id}/renew/ — extends end_date by one more plan cycle from today (or old end_date if still in future)."""
        membership = self.get_object()
        plan = membership.plan
        base_date = max(membership.end_date, timezone.now().date())

        if plan.duration_unit == MembershipPlan.DurationUnit.MONTHS:
            new_end_date = base_date + relativedelta(months=plan.duration_value)
        else:
            new_end_date = base_date + timedelta(days=plan.duration_value)

        membership.end_date = new_end_date
        membership.status = Membership.Status.ACTIVE
        membership.save()

        return Response(MembershipSerializer(membership).data)


class MembershipFreezeViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only — freezes are created via the /freeze/ action above, not directly."""
    queryset = MembershipFreeze.objects.select_related('membership').all()
    serializer_class = MembershipFreezeSerializer
    permission_classes = [IsAuthenticated]