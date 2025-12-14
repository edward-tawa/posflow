from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from company.models.company_model import Company
from branch.models.branch_model import Branch
from customers.models.customer_model import Customer
from users.models import User
from sales.models.sale_model import Sale
from sales.models.sales_invoice_model import SalesInvoice
from sales.models.sales_receipt_model import SalesReceipt


class SaleSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        required=True
    )

    class Meta:
        model = Sale
        fields = [
            'id',
            'company',
            'company_summary',
            'branch',
            'customer',
            'sales_invoice',
            'sales_receipt',
            'sales_date',
            'payment_status',
            'total_amount',
            'tax_amount',
            'sale_type',
            'sale_number',
            'issued_by',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'sale_number',
            'total_amount', 'tax_amount', 'payment_status'
        ]

    def get_company_summary(self, obj):
        return {
            'id': obj.company.id,
            'name': obj.company.name
        }

    def validate(self, attrs):
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if attrs.get('company') and attrs['company'].id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update Sale for company {attrs['company'].id}."
            )
            raise serializers.ValidationError(
                "You cannot create or update a sale for a company other than your own."
            )

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        validated_data['company'] = expected_company  # Force company

        try:
            sale = Sale.objects.create(**validated_data)
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.info(f"Sale '{sale.sale_number}' created for company '{expected_company.name}' by {actor}.")
            return sale
        except Exception as e:
            logger.error(f"Error creating Sale for company '{expected_company.name}' by {actor}: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the sale.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        # Prevent changing company and sale_number
        validated_data.pop('company', None)
        validated_data.pop('sale_number', None)

        if instance.company != expected_company:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(
                f"{actor} attempted to update Sale {instance.id} outside their company."
            )
            raise serializers.ValidationError("You cannot update a sale outside your company.")

        instance = super().update(instance, validated_data)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"Sale '{instance.sale_number}' updated by {actor}.")
        return instance
