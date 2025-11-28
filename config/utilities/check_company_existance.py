from company.models import Company

def check_existance(company_data):
    """
    Check if a company exists based on provided data on company registration.
    """ 
    company = Company.objects.filter(email = company_data.get('email')).values().first()
    if company:
        return True
    return False