from rest_framework.permissions import BasePermission, SAFE_METHODS

class BranchPermissions(BasePermission):
    """
    Custom permission:
    - SAFE_METHODS: allowed for Sales, Marketing, Manager, staff, superuser
    - Editing: only Manager, staff, superuser
    - Branch must belong to user's company
    """

    VIEW_ROLES = ['Sales', 'Marketing', 'Manager']
    EDIT_ROLES = ['Manager']

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Allow safe methods for VIEW_ROLES + staff/superuser
        if request.method in SAFE_METHODS:
            return user.role in self.VIEW_ROLES or user.is_staff or user.is_superuser
        # Allow editing only for EDIT_ROLES + staff/superuser
        return user.role in self.EDIT_ROLES or user.is_staff or user.is_superuser

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        # Object must belong to user's company
        if obj.company != getattr(user, 'company', None):
            return False

        # Allow SAFE_METHODS for view roles
        if request.method in SAFE_METHODS:
            return user.role in self.VIEW_ROLES or user.is_staff or user.is_superuser

        # Editing allowed for EDIT_ROLES + staff/superuser
        return user.role in self.EDIT_ROLES or user.is_staff or user.is_superuser
