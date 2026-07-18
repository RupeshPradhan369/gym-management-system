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