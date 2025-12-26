from rest_framework import serializers
from company.serializers.company_summary_serializer import CompanySummarySerializer
from inventory.models.product_model import Product


class ProductSummarySerializer(serializers.ModelSerializer):
    company = CompanySummarySerializer(read_only=True)
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'company',
            'price',
            'stock',

        ]
        read_only_fields = ['id']