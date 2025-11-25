from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from company.models.company_model import Company
from branch.models.branch_model import Branch
from users.models import User
from sales.models.sales_order_model import SalesOrder
from sales.models.sales_payment_model import SalesPayment


class SalesPaymentSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        required=True
    )

    class Meta:
        model = SalesPayment
        fields = [
            'id',
            'company',
            'company_summary',
            'branch',
            'sales_order',
            'payment_number',
            'payment_date',
            'amount',
            'payment_method',
            'processed_by',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'payment_number', 'payment_date']

    def get_company_summary(self, obj):
        return {
            'id': obj.company.id,
            'name': obj.company.name
        }

    def validate(self, attrs):
        """Validate amount and payment method within company context"""
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if attrs.get('company') and attrs['company'].id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update SalesPayment for company {attrs['company'].id}."
            )
            raise serializers.ValidationError(
                "You cannot create or update a sales payment for a company other than your own."
            )

        # Validate amount
        amount = attrs.get('amount')
        if amount is not None and amount <= 0:
            raise serializers.ValidationError("Payment amount must be greater than zero.")

        # Validate payment method
        payment_method = attrs.get('payment_method')
        valid_methods = [choice[0] for choice in SalesPayment.Method.choices]
        if payment_method is not None and payment_method not in valid_methods:
            raise serializers.ValidationError(f"Invalid payment method: {payment_method}")

        return attrs

    def create(self, validated_data):
        """Create a new SalesPayment with logging and company enforcement"""
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        validated_data['company'] = expected_company  # Force company

        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        sales_order = validated_data.get('sales_order')

        try:
            payment = SalesPayment.objects.create(**validated_data)
            logger.info(
                f"SalesPayment '{payment.payment_number}' for order '{sales_order.order_number}' "
                f"created for company '{expected_company.name}' by {actor}."
            )
            return payment
        except Exception as e:
            logger.error(
                f"Error creating SalesPayment for order '{sales_order.order_number}' "
                f"for company '{expected_company.name}' by {actor}: {str(e)}"
            )
            raise serializers.ValidationError("An error occurred while creating the sales payment.")

    def update(self, instance, validated_data):
        """Update an existing SalesPayment with company validation and logging"""
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        # Prevent changes to company and payment_number
        validated_data.pop('company', None)
        validated_data.pop('payment_number', None)

        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if instance.company != expected_company:
            logger.warning(
                f"{actor} attempted to update SalesPayment {instance.id} outside their company."
            )
            raise serializers.ValidationError("You cannot update a sales payment outside your company.")

        instance = super().update(instance, validated_data)
        logger.info(
            f"SalesPayment '{instance.payment_number}' updated by '{actor}'."
        )
        return instance
