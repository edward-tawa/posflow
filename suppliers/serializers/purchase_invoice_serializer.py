from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from company.models.company_model import Company
from branch.models.branch_model import Branch
from users.models import User
from suppliers.models.purchase_invoice_model import PurchaseInvoice
from suppliers.models.supplier_model import Supplier
from suppliers.models.purchase_order_model import PurchaseOrder


class PurchaseInvoiceSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PurchaseInvoice
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'supplier',
            'purchase_order',
            'invoice_number',
            'invoice_date',
            'currency',
            'total_amount',
            'balance',
            'issued_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'invoice_number', 'invoice_date', 'balance']

    def get_company_summary(self, obj):
        return {
            'id': obj.company.id,
            'name': obj.company.name
        }
    
    def get_branch_summary(self, obj):
        return {
            'id': obj.branch.id,
            'name': obj.branch.name
        }

    def validate(self, attrs):
        """Validate total_amount within company context"""
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        # Enforce company
        if attrs.get('company') and attrs['company'].id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update PurchaseInvoice for company {attrs['company'].id}."
            )
            raise serializers.ValidationError(
                "You cannot create or update a purchase invoice for a company other than your own."
            )

        # Validate total_amount
        total_amount = attrs.get('total_amount')
        if total_amount is not None and total_amount <= 0:
            raise serializers.ValidationError("Invoice total amount must be greater than zero.")

        return attrs

    def create(self, validated_data):
        """Create a new PurchaseInvoice with logging and company enforcement"""
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        validated_data['company'] = expected_company  # Force company
        validated_data['branch'] = request.user.branch

        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        supplier = validated_data.get('supplier')
        purchase_order = validated_data.get('purchase_order')

        try:
            invoice = PurchaseInvoice.objects.create(**validated_data)
            logger.info(
                f"PurchaseInvoice '{invoice.invoice_number}' for supplier '{supplier}' "
                f"created for company '{expected_company.name}' by {actor} "
                f"linked to order '{purchase_order}'."
            )
            return invoice
        except Exception as e:
            logger.error(
                f"Error creating PurchaseInvoice for supplier '{supplier}' "
                f"for company '{expected_company.name}' by {actor}: {str(e)}"
            )
            raise serializers.ValidationError("An error occurred while creating the purchase invoice.")

    def update(self, instance, validated_data):
        """Update an existing PurchaseInvoice with company validation and logging"""
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        # Prevent changes to company and invoice_number
        validated_data.pop('company', None)
        validated_data.pop('invoice_number', None)

        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if instance.company != expected_company:
            logger.warning(
                f"{actor} attempted to update PurchaseInvoice {instance.id} outside their company."
            )
            raise serializers.ValidationError("You cannot update a purchase invoice outside your company.")

        instance = super().update(instance, validated_data)
        logger.info(
            f"PurchaseInvoice '{instance.invoice_number}' updated by '{actor}'."
        )
        return instance
