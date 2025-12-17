from rest_framework.permissions import BasePermission, SAFE_METHODS
from loguru import logger

class SupplierPaymentPermissions(BasePermission):
    # Custom permission to allow only allowed users from the same company to access or modify suppliers.
    VIEW_ROLES = ['Manager', 'Accounting','Purchasing', 'Procurement', 'Admin']
    EDIT_ROLES = ['Manager', 'Admin']
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user.is_authenticated:
            logger.warning(f"Unauthenticated access attempt to {view.__class__.__name__}")
            return False

        allowed_roles = self.VIEW_ROLES if request.method in SAFE_METHODS else self.EDIT_ROLES
        
        if user.is_staff or user.is_superuser or user.role in allowed_roles:
            return True

        logger.warning(
            f"Permission denied for user '{user.username}' on {view.__class__.__name__} "
            f"with method '{request.method}'"
        )
        return False
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated or obj.payment.company != getattr(user, 'company', None):
            logger.warning(
                f"Object permission denied for user '{user.username if user.is_authenticated else 'Anonymous'}' "
                f"on object '{obj}'"
            )
            return False

        allowed_roles = self.VIEW_ROLES if request.method in SAFE_METHODS else self.EDIT_ROLES
        if user.is_staff or user.is_superuser or user.role in allowed_roles:
            return True

        logger.warning(
            f"Object permission denied for user '{user.username}' on object '{obj}' "
            f"with method '{request.method}'"
        )
        return False