from config.permissions.company_role_base_permission import CompanyRolePermission


class AccountPermission(CompanyRolePermission):
    """
    Custom permission class for Account operations.
    Inherits from CompanyRolePermission to enforce company and role-based access control.
    """
    # Custom permission to allow only allowed users from the same company to access or modify accounts.
    VIEW_ROLES = ['Manager', 'Accounting','Purchasing', 'Procurement', 'Admin']
    EDIT_ROLES = ['Manager', 'Admin']