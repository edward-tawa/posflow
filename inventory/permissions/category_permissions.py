from rest_framework.permissions import BasePermission, SAFE_METHODS



class CategoryPermission(BasePermission):
    # Custom permission to allow only users from the same company to access or modify categories.

    VIEW_ROLES = ['Manager', 'Sales', 'Marketing', 'Admin']
    EDIT_ROLES = ['Manager', 'Admin']

    def has_permission(self, request, view):
        """
        Checks if the user has permission to access certain category views
        """
        user = request.user
        if not user.is_authenticated:
            return False
        else:
            # Allow access to list views if the user is authenticated and is_staff, is_superuser, or belongs to one of the roles
            if request.method in SAFE_METHODS:
                return user.is_staff or user.is_superuser or user.role in self.VIEW_ROLES
            else:
                return user.is_staff or user.is_superuser or user.role in self.EDIT_ROLES
        return False
    
    def has_object_permission(self, request, view, obj):
        # checks if the user has permission to access or modify a specific category object
        user = request.user
        if not user.is_authenticated or obj.company != user.company:
            return False
        if request.method in SAFE_METHODS:
            # Allow access to modify object if the user is authenticated and is_staff, is_superuser, or belongs to editing roles
            return user.is_staff or user.is_superuser or user.role in self.VIEW_ROLES
        return user.is_staff or user.is_superuser or user.role in self.EDIT_ROLES