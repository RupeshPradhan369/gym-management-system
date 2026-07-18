from rest_framework.routers import DefaultRouter
from .views import (
    GoalViewSet, BodyMeasurementViewSet, ProgressReportViewSet,
    ExerciseViewSet, WorkoutPlanViewSet, DietPlanViewSet, TrainerAssignmentViewSet,
)

router = DefaultRouter()
router.register(r'goals', GoalViewSet, basename='goal')
router.register(r'measurements', BodyMeasurementViewSet, basename='measurement')
router.register(r'progress-reports', ProgressReportViewSet, basename='progress-report')
router.register(r'exercises', ExerciseViewSet, basename='exercise')
router.register(r'workout-plans', WorkoutPlanViewSet, basename='workout-plan')
router.register(r'diet-plans', DietPlanViewSet, basename='diet-plan')
router.register(r'trainer-assignments', TrainerAssignmentViewSet, basename='trainer-assignment')

urlpatterns = router.urls