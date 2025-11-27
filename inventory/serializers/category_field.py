from rest_framework import serializers
from inventory.models.product_category_model import ProductCategory




class CategoryField(serializers.Field):
    # A custom field that accepts either a category ID (int) or a category name (str),
    # and returns a Category instance. Optional field.

    def to_internal_value(self, data):

        if not data:
            return None
        if isinstance(data, int):
            try:
                return ProductCategory.objects.get(id=data)
            except ProductCategory.DoesNotExist:
                raise serializers.ValidationError(f'ProductCategory with id {data} does not exist.')
        elif isinstance(data, str):
            try:
                return ProductCategory.objects.get(name__iexact=data.strip())
            except ProductCategory.DoesNotExist:
                raise serializers.ValidationError(f"ProductCategory with name '{data}' does not exist.")
        else:
            raise serializers.ValidationError('ProductCategory must be an integer (ID) or string (name).')
        
    def to_representation(self, value):
        if not value:
            return None
        return {id: value.id, 'name': value.name}