# users/permissions/user_management_permission.py
from rest_framework.permissions import BasePermission

class CompanyAdminOrSuperuserCanManageUsers(BasePermission):
    """
    Permission rules for User management (works for both APIView and ViewSet):
    - Superuser can manage all users.
    - Company admin (is_staff=True) can manage users within their company only.
    - Regular users can only view/update themselves.
    """

    message = "You do not have permission to manage these users."

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_staff:
            if request.method == 'POST':
                return getattr(request.user, 'is_superuser', False)  # only superuser can create
            return True
        elif request.user.is_authenticated and request.method == 'GET':
            return True
        return False


    def has_object_permission(self, request, view, obj):
        # Superuser can manage any user
        if request.user.is_superuser:
            return True

        # Company admin can manage users in their own company
        if request.user.is_staff:
            return getattr(obj, 'company', None) == getattr(request.user, 'company', None)

        # Regular user can only view/update themselves
        return obj == request.user
