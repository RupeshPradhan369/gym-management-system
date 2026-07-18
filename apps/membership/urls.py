from rest_framework.routers import DefaultRouter
from .views import MembershipPlanViewSet, MembershipViewSet, MembershipFreezeViewSet

router = DefaultRouter()
router.register(r'plans', MembershipPlanViewSet, basename='membership-plan')
router.register(r'memberships', MembershipViewSet, basename='membership')
router.register(r'freezes', MembershipFreezeViewSet, basename='membership-freeze')

urlpatterns = router.urls