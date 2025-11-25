from config.utilities import get_logged_in_company


def get_expected_company(request):
    """
    Returns the expected company for the logged-in entity from the request.
    """
    user = request.user
    company = get_logged_in_company(request)

    return company or user.company