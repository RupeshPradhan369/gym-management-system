from datetime import timedelta
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Attendance, StaffAttendance, QRToken
from .serializers import AttendanceSerializer, StaffAttendanceSerializer, QRTokenSerializer
from apps.identity.permissions import IsAdminOrReceptionist

QR_VALIDITY_SECONDS = 120  # 2 minutes


class GenerateQRView(APIView):
    """
    GET /attendance/qr/generate/ — member requests a fresh QR token to show
    the gym's scanner. Only usable by the member themselves.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'member':
            return Response({'detail': 'Only members can generate check-in QR codes.'}, status=403)

        token = QRToken.objects.create(
            member=request.user,
            expires_at=timezone.now() + timedelta(seconds=QR_VALIDITY_SECONDS),
        )
        return Response(QRTokenSerializer(token).data, status=201)


class CheckInView(APIView):
    """
    POST /attendance/check-in/  body: {"token": "<uuid>"}
    Scanner app (receptionist device) posts the scanned token here.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token_value = request.data.get('token')
        if not token_value:
            return Response({'detail': 'token is required.'}, status=400)

        try:
            qr = QRToken.objects.get(token=token_value)
        except (QRToken.DoesNotExist, ValueError):
            return Response({'detail': 'Invalid token.'}, status=400)

        if not qr.is_valid():
            return Response({'detail': 'Token expired or already used.'}, status=400)

        qr.is_used = True
        qr.save()

        attendance = Attendance.objects.create(member=qr.member, method=Attendance.Method.QR)
        return Response(AttendanceSerializer(attendance).data, status=201)


class ManualCheckInView(APIView):
    """
    POST /attendance/manual-check-in/  body: {"member": <id>}
    Fallback for receptionist when QR/app isn't available.
    """
    permission_classes = [IsAdminOrReceptionist]

    def post(self, request):
        member_id = request.data.get('member')
        if not member_id:
            return Response({'detail': 'member is required.'}, status=400)

        attendance = Attendance.objects.create(
            member_id=member_id,
            method=Attendance.Method.MANUAL,
            marked_by=request.user,
        )
        return Response(AttendanceSerializer(attendance).data, status=201)


class AttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    """List/retrieve attendance history — members see their own, staff see everyone."""
    queryset = Attendance.objects.select_related('member', 'marked_by').all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'member':
            return self.queryset.filter(member=self.request.user)
        return self.queryset


class StaffAttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StaffAttendance.objects.select_related('staff').all()
    serializer_class = StaffAttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != 'admin':
            return self.queryset.filter(staff=self.request.user)
        return self.queryset