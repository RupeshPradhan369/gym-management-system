from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, MeView, MemberProfileViewSet, StaffProfileViewSet

router = DefaultRouter()
router.register(r'members', MemberProfileViewSet, basename='member')
router.register(r'staff', StaffProfileViewSet, basename='staff')

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', MeView.as_view(), name='me'),
] + router.urls