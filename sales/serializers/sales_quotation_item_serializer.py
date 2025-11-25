from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from inventory.models import Product
from sales.models.sales_quotation_model import SalesQuotation
from sales.models.sales_quotation_item_model import SalesQuotationItem


class SalesQuotationItemSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    product_summary = serializers.SerializerMethodField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    company_summary = serializers.SerializerMethodField(read_only=True)
    company = serializers.PrimaryKeyRelatedField(
        queryset=SalesQuotation._meta.get_field('company').related_model.objects.all(),
        required=True
    )

    class Meta:
        model = SalesQuotationItem
        fields = [
            'id',
            'company',
            'company_summary',
            'sales_quotation',
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
            'id', 'sales_quotation', 'subtotal', 'tax_amount', 'total_price',
            'created_at', 'updated_at'
        ]

    def get_company_summary(self, obj):
        return {
            'id': obj.sales_quotation.company.id,
            'name': obj.sales_quotation.company.name
        }

    def get_product_summary(self, obj):
        return {
            'id': obj.product.id,
            'name': obj.product.name,
            'sku': getattr(obj.product, 'sku', None)
        }

    def validate(self, attrs):
        """Custom validation for company context, quantity, unit_price, and tax_rate"""
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        # Enforce company consistency
        company = attrs.get('company')
        if company and company.id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update SalesQuotationItem for company {company.id}."
            )
            raise serializers.ValidationError(
                "You cannot create or update a sales quotation item for a company other than your own."
            )

        # Validate quantity, unit_price, tax_rate
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
        user = getattr(request, 'user', None)
        validated_data['company'] = expected_company  # Force company

        product = validated_data.get('product')

        try:
            item = SalesQuotationItem.objects.create(**validated_data)
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.info(f"SalesQuotationItem for product '{product.name}' created by '{actor}'.")
            return item
        except Exception as e:
            logger.error(f"Error creating SalesQuotationItem for product '{product.name}': {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the sales quotation item.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        validated_data.pop('company', None)  # Prevent changing company
        validated_data.pop('sales_quotation', None)  # Prevent changing quotation

        if instance.sales_quotation.company != expected_company:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(
                f"{actor} attempted to update SalesQuotationItem {instance.id} outside their company."
            )
            raise serializers.ValidationError("You cannot update a sales quotation item outside your company.")

        instance = super().update(instance, validated_data)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"SalesQuotationItem for product '{instance.product.name}' updated by '{actor}'.")
        return instance
