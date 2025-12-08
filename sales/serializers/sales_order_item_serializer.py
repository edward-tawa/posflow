from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from inventory.models import Product
from sales.models.sales_order_item_model import SalesOrderItem
from sales.models.sales_order_model import SalesOrder


class SalesOrderItemSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    product_summary = serializers.SerializerMethodField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    sales_order_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SalesOrderItem
        fields = [
            'id',
            'sales_order',
            'sales_order_summary',
            'product',
            'product_summary',
            'product_name',
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
        return {
            'id': obj.product.id,
            'name': obj.product.name,
            'sku': getattr(obj.product, 'sku', None)
        }

    def get_sales_order_summary(self, obj):
        return {
            'id': obj.sales_order.id,
            'order_number': obj.sales_order.order_number,
            'customer_name': obj.sales_order.customer_name,
        }

    def validate(self, attrs):
        quantity = attrs.get('quantity')
        unit_price = attrs.get('unit_price')
        tax_rate = attrs.get('tax_rate')

        if quantity is not None and quantity <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        if unit_price is not None and unit_price < 0:
            raise serializers.ValidationError("Unit price cannot be negative.")
        if tax_rate is not None and not (0 <= tax_rate <= 100):
            raise serializers.ValidationError("Tax rate must be between 0 and 100.")

        # Company validation
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        sales_order = attrs.get('sales_order')
        if sales_order and sales_order.company.id != expected_company.id:
            actor = getattr(request.user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.error(f"{actor} attempted to create/update SalesOrderItem for a sales order outside their company.")
            raise serializers.ValidationError("You cannot create or update an item for a sales order outside your company.")

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        validated_data['sales_order'] = validated_data['sales_order']  # enforce company via validation above
        product = validated_data.get('product')

        try:
            item = SalesOrderItem.objects.create(**validated_data)
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.info(f"SalesOrderItem '{product.name}' created by {actor}.")
            return item
        except Exception as e:
            logger.error(f"Error creating SalesOrderItem '{product.name}' by {actor}: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the sales order item.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        validated_data.pop('sales_order', None)  # prevent switching order

        if instance.sales_order.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to update SalesOrderItem '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot update an item outside your company.")

        instance = super().update(instance, validated_data)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"SalesOrderItem '{instance.product_name}' updated by {actor}.")
        return instance
