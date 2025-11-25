from company.models import Company

def check_existance(company_data):
    company = Company.objects.filter(email = company_data.get('email')).values().first()
    if company:
        return True
    return False