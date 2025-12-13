from rest_framework import serializers
from inventory.models import Product
from sales.models.sales_receipt_item_model import SalesReceiptItem
from loguru import logger


class SalesReceiptItemSerializer(serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    product_summary = serializers.SerializerMethodField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = SalesReceiptItem
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'sales_receipt',
            'product',
            'product_summary',
            'quantity',
            'unit_price',
            'tax_rate',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_product_summary(self, obj):
        """Return a summary of the related product"""
        return {
            'id': obj.product.id,
            'name': obj.product.name,
            'sku': getattr(obj.product, 'sku', None)
        }

    def get_company_summary(self, obj):
        return {
            'id': obj.sales_receipt.company.id,
            'name': obj.sales_receipt.company.name
        }
    
    def get_branch_summary(self, obj):
        return {
            'id': obj.sales_receipt.branch.id,
            'name': obj.sales_receipt.branch.name
        }


    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        product = validated_data.get('product')

        try:
            item = SalesReceiptItem.objects.create(**validated_data)
            actor = getattr(user, 'username', 'Unknown')
            logger.info(
                f"SalesReceiptItem for product '{product.name}' created by '{actor}'."
            )
            return item
        except Exception as e:
            logger.error(f"Error creating SalesReceiptItem for product '{product.name}': {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the sales receipt item.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        instance = super().update(instance, validated_data)
        actor = getattr(user, 'username', 'Unknown')
        logger.info(
            f"SalesReceiptItem for product '{instance.product.name}' updated by '{actor}'."
        )
        return instance
