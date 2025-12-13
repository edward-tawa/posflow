from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from company.models.company_model import Company
from branch.models.branch_model import Branch
from users.models import User
from suppliers.models.purchase_payment_model import PurchasePayment
from suppliers.models.supplier_model import Supplier


class PurchasePaymentSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PurchasePayment
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'supplier',
            'payment',
            'payment_date',
            'amount_paid',
            'created_at',
            'updated_at',
            'purchase_invoice'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'payment_date']

    def get_company_summary(self, obj):
        return {
            'id': obj.payment.company.id,
            'name': obj.payment.company.name
        }

    def get_branch_summary(self, obj):
        return {
            'id': obj.payment.branch.id,
            'name': obj.payment.branch.name
        }
    
    def validate(self, attrs):
        """Validate total_amount and payment method within company context"""
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        # Enforce company
        if attrs.get('company') and attrs['company'].id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update PurchasePayment for company {attrs['company'].id}."
            )
            raise serializers.ValidationError(
                "You cannot create or update a purchase payment for a company other than your own."
            )

        # Validate total_amount
        amount = attrs.get('total_amount')
        if amount is not None and amount <= 0:
            raise serializers.ValidationError("Payment amount must be greater than zero.")

        # Validate payment method
        # payment_method = attrs.get('payment_method')
        # valid_methods = [choice[0] for choice in PurchasePayment.Method.choices]
        # if payment_method is not None and payment_method not in valid_methods:
        #     raise serializers.ValidationError(f"Invalid payment method: {payment_method}")

        return attrs

    def create(self, validated_data):
        """Create a new PurchasePayment with logging and company enforcement"""
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        validated_data['company'] = expected_company  # Force company

        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        supplier = validated_data.get('supplier')

        try:
            validated_data.pop('company')
            logger.info(validated_data)
            payment = PurchasePayment.objects.create(**validated_data)
            logger.info(
                f"PurchasePayment '{payment.payment.payment_number}' for supplier '{supplier}' "
                f"created for company '{expected_company.name}' by {actor}."
            )
            return payment
        except Exception as e:
            logger.error(
                f"Error creating PurchasePayment for supplier '{supplier}' "
                f"for company '{expected_company.name}' by {actor}: {str(e)}"
            )
            raise serializers.ValidationError("An error occurred while creating the purchase payment.")

    def update(self, instance, validated_data):
        """Update an existing PurchasePayment with company validation and logging"""
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        # Prevent changes to company and purchase_payment_number
        validated_data.pop('company', None)
        validated_data.pop('purchase_payment_number', None)

        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if instance.company != expected_company:
            logger.warning(
                f"{actor} attempted to update PurchasePayment {instance.id} outside their company."
            )
            raise serializers.ValidationError("You cannot update a purchase payment outside your company.")

        instance = super().update(instance, validated_data)
        logger.info(
            f"PurchasePayment '{instance.purchase_payment_number}' updated by '{actor}'."
        )
        return instance
