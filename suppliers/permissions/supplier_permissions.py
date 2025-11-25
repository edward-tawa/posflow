from config.permissions.company_role_base_permission import CompanyRolePermission


class SupplierPermissions(CompanyRolePermission):
    # Custom permission to allow only allowed users from the same company to access or modify suppliers.
    VIEW_ROLES = ['Manager', 'Accounting','Purchasing', 'Procurement', 'Admin']
    EDIT_ROLES = ['Manager', 'Admin']
    