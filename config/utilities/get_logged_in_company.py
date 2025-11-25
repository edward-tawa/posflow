from company.models.company_model import Company

def get_logged_in_company(request):
    """
    Returns the company instance for the currently logged-in entity.
    
    - If the logged-in entity is a Company, returns the company itself.
    
    - Returns None if entity logged in is not a Company.
    """
    user = getattr(request, 'user', None)

    if not user or not user.is_authenticated:
        raise ValueError("Authentication required.")

    if isinstance(user, Company):
        return user

    return None
