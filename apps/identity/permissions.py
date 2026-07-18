from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only role=admin users pass."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')


class IsAdminOrReceptionist(BasePermission):
    """Admins and receptionists — the two roles that register new members."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ('admin', 'receptionist')
        )


class IsOwnerOrStaff(BasePermission):
    """
    Members can only view/edit their own profile.
    Staff (admin/receptionist/trainer) can view/edit any.
    Used on object-level checks (e.g. retrieving a specific MemberProfile).
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role != 'member':
            return True
        return obj.user_id == request.user.id
    

class IsTrainer(BasePermission):
    """Only role=trainer users pass — used for creating workout/diet plans."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'trainer')
    

class IsAssignedTrainerOrOwnerOrAdmin(BasePermission):
    """
    For fitness object-level checks:
    - admin: full access
    - member: only their own data
    - trainer: only data for members they're actively assigned to
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'admin':
            return True
        if user.role == 'member':
            return obj.member_id == user.id
        if user.role == 'trainer':
            from apps.fitness.models import TrainerAssignment
            return TrainerAssignment.objects.filter(
                member_id=obj.member_id, trainer=user, is_active=True
            ).exists()
        return False