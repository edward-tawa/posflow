from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from sales.models.sales_invoice_model import SalesInvoice
from company.models.company_model import Company
from branch.models.branch_model import Branch
from customers.models.customer_model import Customer
from users.models import User


class SalesInvoiceSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SalesInvoice
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'customer',
            'invoice_number',
            'invoice_date',
            'total_amount',
            'issued_by',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'invoice_number', 'invoice_date', 'total_amount', 'created_at', 'updated_at'
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

    def validate(self, attrs):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if attrs.get('company') and attrs['company'].id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update SalesInvoice for company {attrs['company'].id}."
            )
            raise serializers.ValidationError(
                "You cannot create or update a sales invoice for a company other than your own."
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        validated_data['company'] = expected_company  # enforce company
        validated_data['branch'] = request.user.branch
        actor = None
        try:
            invoice = SalesInvoice.objects.create(**validated_data)
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.info(f"SalesInvoice '{invoice.invoice_number}' created for company '{expected_company.name}' by {actor}.")
            return invoice
        except Exception as e:
            logger.error(f"Error creating SalesInvoice for company '{expected_company.name}' by {actor}: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the sales invoice.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        validated_data.pop('company', None)  # prevent switching company
        validated_data.pop('invoice_number', None)  # prevent changing invoice number

        if instance.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to update SalesInvoice '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot update a sales invoice outside your company.")

        instance = super().update(instance, validated_data)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"SalesInvoice '{instance.invoice_number}' updated by {actor}.")
        return instance