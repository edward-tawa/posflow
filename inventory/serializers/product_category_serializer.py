from rest_framework import serializers
from inventory.models.product_category_model import ProductCategory
from company.models.company_model import Company


class ProductCategorySerializer(serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = ProductCategory
        fields = [
            'id',
            'name',
            'company_summary',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_company_summary(self, obj):
        return {
            'id': obj.customer.id,
            'first_name': obj.customer.first_name,
            'last_name': obj.customer.last_name,
            'email': obj.customer.email
        }