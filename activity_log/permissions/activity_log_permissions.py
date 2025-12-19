from rest_framework.permissions import BasePermission, SAFE_METHODS

class ActivityLogPermission(BasePermission):
    """
    POS ActivityLog permission rules:
    - Managers, Staff, Superusers: can view logs of their company.
    - Sales, Marketing: can only view logs of their company.
    - Users cannot access logs from other companies.
    """

    VIEW_ROLES = ['Sales', 'Marketing', 'Manager']
    EDIT_ROLES = ['Manager']

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            # Any role allowed to view (Sales, Marketing, Manager) plus staff/superuser
            return request.user.is_staff or request.user.is_superuser or request.user.role in self.VIEW_ROLES
        else:
            # Only roles allowed to edit (Manager) plus staff/superuser
            return request.user.is_staff or request.user.is_superuser or request.user.role in self.EDIT_ROLES

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if not hasattr(obj, 'company'):
            return False  # Safety check

        # Restrict access to customers of the same company
        if obj.company != request.user.company:
            return False

        if request.method in SAFE_METHODS:
            # View: staff, superuser, or roles in VIEW_ROLES
            return request.user.is_staff or request.user.is_superuser or request.user.role in self.VIEW_ROLES
        else:
            # Edit: staff, superuser, or Managers
            return request.user.is_staff or request.user.is_superuser or request.user.role == 'Manager'
