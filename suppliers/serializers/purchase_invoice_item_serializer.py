from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from suppliers.models.purchase_invoice_item_model import PurchaseInvoiceItem
from suppliers.models.purchase_invoice_model import PurchaseInvoice
from inventory.models.product_model import Product
from company.models.company_model import Company


class PurchaseInvoiceItemSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    purchase_invoice_summary = serializers.SerializerMethodField(read_only=True)
    product_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PurchaseInvoiceItem
        fields = [
            'id',
            'purchase_invoice',
            'purchase_invoice_summary',
            'product',
            'product_summary',
            'quantity',
            'unit_price',
            'total_price',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_price', 'purchase_invoice_summary', 'product_summary']

    def get_purchase_invoice_summary(self, obj):
        return {
            'id': obj.purchase_invoice.id,
            'invoice_number': obj.purchase_invoice.invoice_number,
            'total_amount': obj.purchase_invoice.total_amount,
            'balance': obj.purchase_invoice.balance
        }

    def get_product_summary(self, obj):
        return {
            'id': obj.product.id,
            'name': obj.product.name,
            'tax_rate': getattr(obj.product, 'tax_rate', 0)
        }

    def validate(self, attrs):
        """Validate that the item belongs to the correct company via invoice"""
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        purchase_invoice = attrs.get('purchase_invoice')
        if purchase_invoice and purchase_invoice.company.id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update PurchaseInvoiceItem for invoice {purchase_invoice.id} "
                f"outside their company."
            )
            raise serializers.ValidationError(
                "You cannot create or update an invoice item for an invoice outside your company."
            )

        # Validate quantity
        quantity = attrs.get('quantity')
        if quantity is not None and quantity <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")

        # Validate unit_price
        unit_price = attrs.get('unit_price')
        if unit_price is not None and unit_price <= 0:
            raise serializers.ValidationError("Unit price must be greater than zero.")

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        purchase_invoice = validated_data.get('purchase_invoice')
        product = validated_data.get('product')

        try:
            item = PurchaseInvoiceItem.objects.create(**validated_data)
            logger.info(
                f"PurchaseInvoiceItem for product '{product.name}' added to invoice '{purchase_invoice.invoice_number}' "
                f"by '{actor}'."
            )
            return item
        except Exception as e:
            logger.error(
                f"Error creating PurchaseInvoiceItem for product '{product.name}' "
                f"on invoice '{purchase_invoice.invoice_number}' by '{actor}': {str(e)}"
            )
            raise serializers.ValidationError("An error occurred while creating the purchase invoice item.")

    def update(self, instance, validated_data):
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        # Ensure item belongs to the correct company
        if instance.purchase_invoice.company != expected_company:
            logger.warning(
                f"{actor} attempted to update PurchaseInvoiceItem {instance.id} outside their company."
            )
            raise serializers.ValidationError(
                "You cannot update an invoice item outside your company."
            )

        instance = super().update(instance, validated_data)
        logger.info(
            f"PurchaseInvoiceItem {instance.id} for product '{instance.product.name}' updated by '{actor}'."
        )
        return instance
