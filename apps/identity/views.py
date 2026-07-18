from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, MemberProfile, StaffProfile
from .serializers import UserSerializer, MemberProfileSerializer, StaffProfileSerializer
from .permissions import IsAdmin, IsAdminOrReceptionist, IsOwnerOrStaff


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Adds role/username to the JWT response body, not just inside the token itself."""
    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        data['username'] = self.user.username
        data['user_id'] = self.user.id
        return data


class LoginView(TokenObtainPairView):
    """POST /auth/login/  — returns access + refresh tokens, plus role/username."""
    serializer_class = CustomTokenObtainPairSerializer


class MeView(APIView):
    """GET /auth/me/ — returns the currently logged-in user's info."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class MemberProfileViewSet(viewsets.ModelViewSet):
    """
    /members/          GET (list, staff only), POST (register, admin/receptionist)
    /members/{id}/      GET, PATCH, DELETE
    """
    queryset = MemberProfile.objects.select_related('user').all()
    serializer_class = MemberProfileSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminOrReceptionist()]
        if self.action in ('retrieve', 'update', 'partial_update'):
            return [IsAuthenticated(), IsOwnerOrStaff()]
        return [IsAdminOrReceptionist()]

    def get_queryset(self):
        # Members only ever see their own profile in a list; staff see everyone.
        if self.request.user.role == 'member':
            return self.queryset.filter(user=self.request.user)
        return self.queryset


class StaffProfileViewSet(viewsets.ModelViewSet):
    """
    /staff/             GET (list, admin only), POST (create staff, admin only)
    /staff/{id}/         GET, PATCH, DELETE
    """
    queryset = StaffProfile.objects.select_related('user').all()
    serializer_class = StaffProfileSerializer
    permission_classes = [IsAdmin]