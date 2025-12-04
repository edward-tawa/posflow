from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from taxes.models.fiscal_invoice_model import FiscalInvoice
from taxes.models.fiscalisation_response_model import FiscalisationResponse
from company.models.company_model import Company

class FiscalisationResponseSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    fiscal_invoice_summary = serializers.SerializerMethodField(read_only=True)
    company_summary = serializers.SerializerMethodField(read_only=True)

    fiscal_invoice = serializers.PrimaryKeyRelatedField(queryset=FiscalInvoice.objects.all(), required=True)

    class Meta:
        model = FiscalisationResponse
        fields = [
            'id',
            'fiscal_invoice',
            'fiscal_invoice_summary',
            'company_summary',
            'response_code',
            'response_message',
            'fiscal_code',
            'qr_code',
            'raw_response',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'fiscal_invoice_summary',
            'company_summary',
            'created_at',
            'updated_at',
        ]

    def get_fiscal_invoice_summary(self, obj):
        if obj.fiscal_invoice:
            return {
                'id': obj.fiscal_invoice.id,
                'invoice_number': getattr(obj.fiscal_invoice, 'invoice_number', str(obj.fiscal_invoice)),
            }
        return None

    def get_company_summary(self, obj):
        if obj.fiscal_invoice and obj.fiscal_invoice.company:
            return {
                'id': obj.fiscal_invoice.company.id,
                'name': obj.fiscal_invoice.company.name,
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
                f"{actor} attempted to create/update FiscalizationResponse for a fiscal invoice outside their company."
            )
            raise serializers.ValidationError(
                "You cannot create or update a fiscalization response for a fiscal invoice outside your company."
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        try:
            response = FiscalisationResponse.objects.create(**validated_data)
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.info(f"FiscalisationResponse '{response.id}' created for FiscalInvoice '{response.fiscal_invoice.invoice_number}' by {actor}.")
            return response
        except Exception as e:
            logger.error(f"Error creating FiscalisationResponse for FiscalInvoice '{validated_data.get('fiscal_invoice')}' by {actor}: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the fiscalisation response.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        # Prevent switching fiscal invoice
        validated_data.pop('fiscal_invoice', None)

        if instance.fiscal_invoice.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to update FiscalisationResponse '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot update a fiscalisation response outside your company.")

        instance = super().update(instance, validated_data)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"FiscalizationResponse '{instance.id}' updated by {actor}.")
        return instance

    def delete(self):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        instance = self.instance

        if instance.fiscal_invoice.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to delete FiscalizationResponse '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot delete a fiscalization response outside your company.")

        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"FiscalizationResponse '{instance.id}' deleted by {actor}.")
        instance.delete()
