from rest_framework import serializers
from inventory.models import Product
from suppliers.models.purchase_return_item_model import PurchaseReturnItem
from loguru import logger
from decimal import Decimal, ROUND_HALF_UP


class PurchaseReturnItemSerializer(serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    product_summary = serializers.SerializerMethodField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = PurchaseReturnItem
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'purchase_return',
            'product',
            'product_summary',
            'quantity',
            'unit_price',
            'tax_rate',
            'subtotal',
            'tax_amount',
            'total_price',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'subtotal', 'tax_amount', 'total_price',
            'created_at', 'updated_at'
        ]

    def get_product_summary(self, obj):
        """Return a brief summary of the related product"""
        return {
            'id': obj.product.id,
            'name': obj.product.name,
            'sku': getattr(obj.product, 'sku', None)
        }

    def get_company_summary(self, obj):
        return {
            'id': obj.product.company.id,
            'name': obj.product.company.name,
           
        }
    
    def get_branch_summary(self, obj):
        return {
            'id': obj.product.branch.id,
            'name': obj.product.branch.name,
           
        }

    def validate(self, attrs):
        """Custom validation for quantity, unit_price, and tax_rate"""
        quantity = attrs.get('quantity')
        unit_price = attrs.get('unit_price')
        tax_rate = attrs.get('tax_rate')

        if quantity is not None and quantity <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        if unit_price is not None and unit_price < 0:
            raise serializers.ValidationError("Unit price cannot be negative.")
        if tax_rate is not None and not (0 <= tax_rate <= 100):
            raise serializers.ValidationError("Tax rate must be between 0 and 100.")

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        product = validated_data.get('product')

        try:
            item = PurchaseReturnItem.objects.create(**validated_data)
            actor = getattr(user, 'username', 'Unknown')
            logger.info(f"PurchaseReturnItem for product '{product.name}' created by '{actor}'.")
            return item
        except Exception as e:
            logger.error(f"Error creating PurchaseReturnItem for product '{product.name}': {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the purchase return item.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        instance = super().update(instance, validated_data)
        actor = getattr(user, 'username', 'Unknown')
        logger.info(f"PurchaseReturnItem for product '{instance.product.name}' updated by '{actor}'.")
        return instance
