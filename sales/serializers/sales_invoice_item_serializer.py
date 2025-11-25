from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from sales.models.sales_invoice_item_model import SalesInvoiceItem
from inventory.models import Product


class SalesInvoiceItemSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    product_summary = serializers.SerializerMethodField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = SalesInvoiceItem
        fields = [
            'id',
            'sales_invoice',
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
            'id', 'sales_invoice', 'subtotal', 'tax_amount', 'total_price',
            'created_at', 'updated_at'
        ]

    def get_product_summary(self, obj):
        return {
            'id': obj.product.id,
            'name': obj.product.name,
            'sku': getattr(obj.product, 'sku', None)
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

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        validated_data['sales_invoice'].company = expected_company  # enforce company
        user = getattr(request, 'user', None)
        product = validated_data.get('product')

        try:
            item = SalesInvoiceItem.objects.create(**validated_data)
            actor = getattr(user, 'username', 'Unknown')
            logger.info(f"SalesInvoiceItem for product '{product.name}' created by '{actor}' in company '{expected_company.name}'.")
            return item
        except Exception as e:
            logger.error(f"Error creating SalesInvoiceItem for product '{product.name}': {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the sales invoice item.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        if instance.sales_invoice.company.id != expected_company.id:
            actor = getattr(user, 'username', 'Unknown')
            logger.warning(f"{actor} attempted to update SalesInvoiceItem '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot update a sales invoice item outside your company.")

        instance = super().update(instance, validated_data)
        actor = getattr(user, 'username', 'Unknown')
        logger.info(f"SalesInvoiceItem '{instance.product_name}' updated by '{actor}' in company '{expected_company.name}'.")
        return instance
