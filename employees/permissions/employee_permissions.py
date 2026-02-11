from rest_framework.permissions import BasePermission, SAFE_METHODS
from employees.models.employee_model import Employee
from loguru import logger


class EmployeePermission(BasePermission):
    """Custom permission:
    - SAFE_METHODS: allowed for Sales, Marketing, Manager, staff, superuser
    - Editing: only Manager, staff, superuser
    - Employee must belong to user's company
    """

    VIEW_ROLES = ['Sales', 'Marketing', 'Manager', 'Employee']
    EDIT_ROLES = ['Manager']

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Allow safe methods for VIEW_ROLES + staff/superuser
        if request.method in SAFE_METHODS: 
            return user.is_staff or user.is_superuser
        return user.is_staff or user.is_superuser

    def has_object_permission(self, request, view, obj):
        user = request.user
     
        if not user or not user.is_authenticated:
            return False
        
        # Object must belong to user's company
        if obj.company != getattr(user, 'company', None):
            return False
        
        # Allow SAFE_METHODS for view roles
        allowed_roles = self.VIEW_ROLES if request.method in SAFE_METHODS else self.EDIT_ROLES
        if user.is_staff or user.is_superuser or user.role in allowed_roles:
            return True