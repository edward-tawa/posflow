from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from suppliers.models.purchase_payment_allocation_model import PurchasePaymentAllocation
from suppliers.models.purchase_payment_model import PurchasePayment
from suppliers.models.purchase_invoice_model import PurchaseInvoice
from suppliers.models.supplier_model import Supplier
from company.models.company_model import Company
from branch.models.branch_model import Branch
from users.models import User


class PurchasePaymentAllocationSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    supplier_summary = serializers.SerializerMethodField(read_only=True)
    purchase_payment_summary = serializers.SerializerMethodField(read_only=True)
    purchase_invoice_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PurchasePaymentAllocation
        fields = [
            'id',
            'company',
            'company_summary',
            'branch_summary',
            'supplier',
            'supplier_summary',
            'purchase_payment',
            'purchase_payment_summary',
            'purchase_invoice',
            'purchase_invoice_summary',
            'allocation_number',
            'allocation_date',
            'allocated_amount',
            'allocated_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'allocation_number', 'allocation_date',
            'company_summary', 'supplier_summary', 'purchase_payment_summary', 'purchase_invoice_summary'
        ]

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

    def get_supplier_summary(self, obj):
        return {
            'id': obj.supplier.id,
            'name': obj.supplier.name
        }

    def get_purchase_payment_summary(self, obj):
        # return {
        #     'id': obj.purchase_payment.id,
        #     'payment_number': obj.purchase_payment.purchase_payment_number,
        #     'total_amount': obj.purchase_payment.total_amount
        # }
        pass

    def get_purchase_invoice_summary(self, obj):
        return {
            'id': obj.purchase_invoice.id,
            'invoice_number': obj.purchase_invoice.invoice_number,
            'total_amount': obj.purchase_invoice.total_amount,
            'balance': obj.purchase_invoice.balance
        }

    def validate(self, attrs):
        """Validate allocated_amount and company ownership"""
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        # Company enforcement
        company = attrs.get('company')
        if company and company.id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update PurchasePaymentAllocation for company {company.id}."
            )
            raise serializers.ValidationError(
                "You cannot create or update a payment allocation for a company other than your own."
            )

        # Validate allocated_amount > 0
        allocated_amount = attrs.get('allocated_amount')
        if allocated_amount is not None and allocated_amount <= 0:
            raise serializers.ValidationError("Allocated amount must be greater than zero.")

        # Validate allocation does not exceed invoice balance
        purchase_invoice = attrs.get('purchase_invoice')
        if purchase_invoice and allocated_amount and allocated_amount > purchase_invoice.balance:
            raise serializers.ValidationError("Allocated amount cannot exceed invoice balance.")

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        validated_data['company'] = expected_company  # Force company

        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        supplier = validated_data.get('supplier')
        invoice = validated_data.get('purchase_invoice')
        payment = validated_data.get('purchase_payment')

        try:
            allocation = PurchasePaymentAllocation.objects.create(**validated_data)
            logger.info(
                f"PurchasePaymentAllocation '{allocation.allocation_number}' of amount '{allocation.allocated_amount}' "
                f"applied to invoice '{invoice.invoice_number}' from payment '{payment.payment.payment_number}' "
                f"for supplier '{supplier.name}' by '{actor}'."
            )
            return allocation
        except Exception as e:
            logger.error(
                f"Error creating PurchasePaymentAllocation for invoice '{invoice.invoice_number}' "
                f"by '{actor}': {str(e)}"
            )
            raise serializers.ValidationError("An error occurred while creating the payment allocation.")

    def update(self, instance, validated_data):
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        # Prevent changes to company and allocation_number
        validated_data.pop('company', None)
        validated_data.pop('allocation_number', None)

        if instance.company != expected_company:
            logger.warning(
                f"{actor} attempted to update PurchasePaymentAllocation {instance.id} outside their company."
            )
            raise serializers.ValidationError(
                "You cannot update a payment allocation outside your company."
            )

        instance = super().update(instance, validated_data)
        logger.info(
            f"PurchasePaymentAllocation '{instance.allocation_number}' updated by '{actor}'."
        )
        return instance
