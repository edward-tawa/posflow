from rest_framework import serializers
from users.models.user_model import User
from company.models import Company
from django.core.exceptions import ObjectDoesNotExist

class CompanyRelatedField(serializers.Field):
    """
    Accepts either company ID (int) or name (str) and returns a Company instance.
    """
    
    def to_internal_value(self, data):
        if isinstance(data, int):
            # Treat as ID
            try:
                return Company.objects.get(id=data)
            except Company.DoesNotExist:
                raise serializers.ValidationError(f"Company with id {data} does not exist.")
        elif isinstance(data, str):
            # Treat as name
            try:
                return Company.objects.get(name=data)
            except Company.DoesNotExist:
                raise serializers.ValidationError(f"Company with name '{data}' does not exist.")
        elif data is None:
            return None
        else:
            raise serializers.ValidationError("Company must be an integer (ID) or string (name).")

    def to_representation(self, value):
        # Return the company ID in API responses
        return value.id if value else None
