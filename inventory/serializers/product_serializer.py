from rest_framework import serializers
from inventory.models.product_model import Product
from company.serializers.company_serializer import CompanySerializer
from inventory.serializers.category_field import CategoryField

class ProductSerializer(serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only = True)
    category = CategoryField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'company_summary',
            'name',
            'description',
            'sku',
            'price',
            'stock',
            'category',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'sku', 'created_at', 'updated_at']

    def get_company_summary(self, obj):
        return {
            'id': obj.company.id,
            'name': obj.company.name
        }

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be a positive value")
        return value
    
    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative")
        return value
    
    def create(self, validated_data):

        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['company'] = request.user.company
            return super().create(validated_data)
        raise serializers.ValidationError("Company information is missing in the request context")
    
    def update(self, instance, validated_data):
        validated_data.pop('company', None)
        return super().update(instance, validated_data)