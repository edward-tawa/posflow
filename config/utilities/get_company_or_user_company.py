from config.utilities.get_logged_in_company import get_logged_in_company
from loguru import logger

def get_expected_company(request):
    """
    Returns the expected company for the logged-in entity from the request.
    """
    user = request.user
    logger.info(f"User log:{user}")
    company = get_logged_in_company(request)

    return company or user.company