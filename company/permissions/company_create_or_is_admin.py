from rest_framework.permissions import BasePermission, SAFE_METHODS

class CompanyCreateOrAdminPermission(BasePermission):
    """
    Permission rules:
    - Anyone can create a company (POST).
    - System superuser can see all companies and manage everything.
    - Company admin (is_staff=True) can manage objects within their own company.
    - Regular staff cannot access company management endpoints outside their scope.
    """
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        # Anyone can create a company
        if request.method == 'POST':
            return True

        # Superuser has full access
        if request.user and request.user.is_superuser:
            return True

        # Company admin access
        if request.user and request.user.is_staff:
            # Allow read-only (SAFE_METHODS) or write methods they can manage
            if request.method in SAFE_METHODS or request.method in ['PATCH', 'DELETE']:
                return True
            # Disallow other methods
            return False

        # Regular users cannot access
        return False

    def has_object_permission(self, request, view, obj):
        """
        Object-level permissions:
        - Superuser can do anything.
        - Company admin can only manage objects related to their company.
        """
        if request.user.is_superuser:
            return True

        if request.user.is_staff:
            # Company objects themselves
            if isinstance(obj, type(request.user)):
                return obj.id == request.user.company.id
            # For objects with a company attribute (e.g., users)
            company = getattr(obj, 'company', None)
            return company == request.user.company

        return False
