from rest_framework import serializers
from inventory.models.product_category_model import ProductCategory
from company.models.company_model import Company


class ProductCategorySerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        required=True
    )#to be removed
    class Meta:
        model = ProductCategory
        fields = [
            'id',
            'name',
            'company',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']