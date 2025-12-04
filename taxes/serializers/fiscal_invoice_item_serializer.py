from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from taxes.models.fiscal_invoice_model import FiscalInvoice
from taxes.models.fiscal_invoice_item_model import FiscalInvoiceItem
from sales.models import SalesOrderItem

class FiscalInvoiceItemSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    fiscal_invoice_summary = serializers.SerializerMethodField(read_only=True)
    sale_item_summary = serializers.SerializerMethodField(read_only=True)
    fiscal_invoice = serializers.PrimaryKeyRelatedField(queryset=FiscalInvoice.objects.all(), required=True)
    sale_item = serializers.PrimaryKeyRelatedField(queryset=SalesOrderItem.objects.all(), required=False, allow_null=True)

    class Meta:
        model = FiscalInvoiceItem
        fields = [
            'id',
            'fiscal_invoice',
            'fiscal_invoice_summary',
            'sale_item',
            'sale_item_summary',
            'description',
            'quantity',
            'unit_price',
            'tax_rate',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'fiscal_invoice_summary',
            'sale_item_summary',
            'created_at',
            'updated_at',
        ]

    def get_fiscal_invoice_summary(self, obj):
        if obj.fiscal_invoice:
            return {
                'id': obj.fiscal_invoice.id,
                'fiscal_code': getattr(obj.fiscal_invoice, 'fiscal_code', None),
            }
        return None

    def get_sale_item_summary(self, obj):
        if obj.sale_item:
            return {
                'id': obj.sale_item.id,
                'description': getattr(obj.sale_item, 'description', str(obj.sale_item)),
            }
        return None

    def validate(self, attrs):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        fiscal_invoice = attrs.get('fiscal_invoice')
        if fiscal_invoice and fiscal_invoice.company.id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update FiscalInvoiceItem for a fiscal invoice outside their company."
            )
            raise serializers.ValidationError(
                "You cannot create or update a fiscal invoice item for a fiscal invoice outside your company."
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        try:
            item = FiscalInvoiceItem.objects.create(**validated_data)
            actor = getattr(user, 'username', None) or getattr(validated_data['fiscal_invoice'].company, 'name', 'Unknown')
            logger.info(f"FiscalInvoiceItem '{item.description}' created for FiscalInvoice '{item.fiscal_invoice.id}' by {actor}.")
            return item
        except Exception as e:
            logger.error(f"Error creating FiscalInvoiceItem for FiscalInvoice '{validated_data.get('fiscal_invoice')}' by {actor}: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the fiscal invoice item.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        # Prevent changing fiscal invoice to another company
        validated_data.pop('fiscal_invoice', None)

        if instance.fiscal_invoice.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to update FiscalInvoiceItem '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot update a fiscal invoice item outside your company.")

        instance = super().update(instance, validated_data)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"FiscalInvoiceItem '{instance.description}' updated by {actor}.")
        return instance

    def delete(self):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        instance = self.instance

        if instance.fiscal_invoice.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to delete FiscalInvoiceItem '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot delete a fiscal invoice item outside your company.")

        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"FiscalInvoiceItem '{instance.description}' deleted by {actor}.")
        instance.delete()
