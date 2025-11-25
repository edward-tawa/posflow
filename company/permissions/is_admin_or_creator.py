from rest_framework.permissions import BasePermission

class IsAdminOrCreator(BasePermission):
    """
    Custom permission for POSFlow:
    - `create` → anyone can create
    - other actions → admin only
    """
    message = "You must be an admin to perform this action."  # custom message

    def has_permission(self, request, view):
        # allows anyone to create
        if view.action == 'create':
            return True
        # other actions require admin privileges
        return request.user and request.user.is_superuser
