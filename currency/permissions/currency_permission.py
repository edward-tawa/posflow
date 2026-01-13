from config.permissions.company_role_base_permission import CompanyRolePermission


class CurrencyPermission(CompanyRolePermission):
    """
    Custom permission class for Currency operations.
    Inherits from CompanyRolePermission to enforce company and role-based access control.
    """
    # Custom permission to allow only allowed users from the same company to access or modify currencies.
    VIEW_ROLES = ['Manager', 'Accounting','Purchasing', 'Procurement', 'Admin']
    EDIT_ROLES = ['Manager', 'Admin']