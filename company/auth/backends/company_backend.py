from django.contrib.auth.backends import ModelBackend
from company.models.company_model import Company

class CompanyBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            company = Company.objects.get(email=email)
            if company.check_password(password):
                return company
        except Company.DoesNotExist:
            return None
