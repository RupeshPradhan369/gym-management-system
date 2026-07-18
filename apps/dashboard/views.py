from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.identity.models import User
from apps.identity.permissions import IsAdmin
from apps.membership.models import Membership
from apps.attendance.models import Attendance
from apps.billing.models import Payment
from django.db import models

class AdminSummaryView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        today = timezone.now().date()
        month_start = today.replace(day=1)

        total_members = User.objects.filter(role=User.Role.MEMBER).count()

        active_memberships = Membership.objects.filter(status=Membership.Status.ACTIVE).count()
        frozen_memberships = Membership.objects.filter(status=Membership.Status.FROZEN).count()
        expired_memberships = Membership.objects.filter(
            status=Membership.Status.ACTIVE, end_date__lt=today
        ).count()
        expiring_soon = Membership.objects.filter(
            status=Membership.Status.ACTIVE,
            end_date__gte=today,
            end_date__lte=today + timezone.timedelta(days=7),
        ).count()

        today_attendance = Attendance.objects.filter(check_in_time__date=today).count()

        successful_payments = Payment.objects.filter(status=Payment.Status.SUCCESS)
        revenue_today = successful_payments.filter(paid_at__date=today).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        revenue_this_month = successful_payments.filter(paid_at__date__gte=month_start).aggregate(
            total=models.Sum('amount')
        )['total'] or 0

        return Response({
            'date': today,
            'total_members': total_members,
            'active_memberships': active_memberships,
            'frozen_memberships': frozen_memberships,
            'expired_but_marked_active': expired_memberships,
            'expiring_within_7_days': expiring_soon,
            'today_attendance_count': today_attendance,
            'revenue_today': revenue_today,
            'revenue_this_month': revenue_this_month,
        })