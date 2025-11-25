from rest_framework import serializers
from company.models.company_model import Company


class CompanyRelatedField(serializers.Field):
    """
    Custom field that accepts either a company ID (int) or a name (str),
    and returns a Company instance. Optional field.
    """
    def to_internal_value(self, data):
        # If no company provided, allow None
        if not data:
            return None

        # Try to find by ID
        if isinstance(data, int):
            try:
                return Company.objects.get(id=data)
            except Company.DoesNotExist:
                raise serializers.ValidationError(f"Company with id {data} does not exist.")

        # Try to find by name
        elif isinstance(data, str):
            try:
                return Company.objects.get(name__iexact=data.strip())
            except Company.DoesNotExist:
                raise serializers.ValidationError(f"Company with name '{data}' does not exist.")

        # Invalid data type
        else:
            raise serializers.ValidationError("Company must be an integer (ID) or string (name).")

    def to_representation(self, value):
        if not value:
            return None
        return {"id": value.id, "name": value.name}
