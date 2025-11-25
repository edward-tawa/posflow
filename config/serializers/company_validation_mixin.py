from rest_framework import serializers
from loguru import logger
from config.utilities.get_logged_in_company import get_logged_in_company

class CompanyValidationMixin:
    """
    Mixin for validating that the 'company' in attrs matches the logged-in company.
    """

    def validate_company(self, company):
        request = self.context.get('request')
        user = getattr(request, "user", None)
        logged_in_company = get_logged_in_company(request)

        expected_company = logged_in_company or getattr(user, "company", None)

        if not expected_company:
            raise serializers.ValidationError("Unable to determine your company context.")

        if company.id != expected_company.id:
            logger.error(
                f"User {getattr(user, 'username', 'Unknown')} from company"
                f"{getattr(expected_company, 'name', 'Unknown')} attempted an invalid company operation "
                f"on company {company.id}."
            )
            raise serializers.ValidationError(
                "You cannot operate on a different company's data."
            )

        return company
