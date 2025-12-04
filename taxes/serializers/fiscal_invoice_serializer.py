from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from company.models.company_model import Company
from branch.models.branch_model import Branch
from taxes.models.fiscal_device_model import FiscalDevice
from taxes.models.fiscal_invoice_model import FiscalInvoice
from sales.models.sales_invoice_model import SalesInvoice 

class FiscalInvoiceSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    device_summary = serializers.SerializerMethodField(read_only=True)
    sales_invoice_summary = serializers.SerializerMethodField(read_only=True)

    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=True)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=True)
    device = serializers.PrimaryKeyRelatedField(queryset=FiscalDevice.objects.all(), required=False, allow_null=True)
    sale = serializers.PrimaryKeyRelatedField(queryset=SalesInvoice.objects.all(), required=True)  # link to actual POS sale

    class Meta:
        model = FiscalInvoice
        fields = [
            'id',
            'company',
            'company_summary',
            'branch',
            'branch_summary',
            'device',
            'device_summary',
            'sale',
            'sales_invoice_summary',
            'invoice_number',
            'total_amount',
            'total_tax',
            'is_fiscalized',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'company_summary',
            'branch_summary',
            'device_summary',
            'sales_invoice_summary',
            'created_at',
            'updated_at',
        ]

    def get_company_summary(self, obj):
        return {'id': obj.company.id, 'name': obj.company.name}

    def get_branch_summary(self, obj):
        return {'id': obj.branch.id, 'name': getattr(obj.branch, 'name', str(obj.branch))}

    def get_device_summary(self, obj):
        if obj.device:
            return {
                'id': obj.device.id,
                'device_name': obj.device.device_name,
                'device_serial_number': obj.device.device_serial_number,
            }
        return None

    def get_sales_invoice_summary(self, obj):
        if obj.sale:
            return {
                'id': obj.sale.id,
                'invoice_number': getattr(obj.sale, 'invoice_number', str(obj.sale)),
            }
        return None

    def validate(self, attrs):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if attrs.get('company') and attrs['company'].id != expected_company.id:
            logger.error(f"{actor} attempted to create/update FiscalInvoice for company {attrs['company'].id}.")
            raise serializers.ValidationError(
                "You cannot create or update a fiscal invoice for a company other than your own."
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        validated_data['company'] = expected_company  # enforce company

        try:
            invoice = FiscalInvoice.objects.create(**validated_data)
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.info(f"FiscalInvoice '{invoice.invoice_number}' created for company '{expected_company.name}' by {actor}.")
            return invoice
        except Exception as e:
            logger.error(f"Error creating FiscalInvoice for company '{expected_company.name}' by {actor}: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the fiscal invoice.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        # Prevent switching company
        validated_data.pop('company', None)

        if instance.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to update FiscalInvoice '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot update a fiscal invoice outside your company.")

        instance = super().update(instance, validated_data)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"FiscalInvoice '{instance.invoice_number}' updated by {actor}.")
        return instance

    def delete(self):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        instance = self.instance

        if instance.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to delete FiscalInvoice '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot delete a fiscal invoice outside your company.")

        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"FiscalInvoice '{instance.invoice_number}' deleted by {actor}.")
        instance.delete()
