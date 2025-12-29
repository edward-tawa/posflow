from rest_framework import serializers
from sales.models.sales_quotation_model import SalesQuotation
from company.models.company_model import Company
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger


class SalesQuotationSerializer(serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SalesQuotation
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'customer',
            'quotation_number',
            'quotation_date',
            'valid_until',
            'total_amount',
            'status',
            'created_by',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'company_summary', 'quotation_number', 'total_amount',
            'quotation_date', 'created_at', 'updated_at'
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
        """Validate that the company matches the logged-in user's company"""
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        company = attrs.get('company', expected_company)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if company.id != expected_company.id:
            logger.error(f"{actor} attempted to create/update SalesQuotation for company {company.id}.")
            raise serializers.ValidationError("You cannot create or update a sales quotation outside your company.")
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        company = get_expected_company(request)
        validated_data['company'] = company
        validated_data['branch'] = request.user.branch
        actor = None
        try:
            quotation = SalesQuotation.objects.create(**validated_data)
            actor = getattr(user, 'username', 'Unknown')
            logger.info(f"SalesQuotation '{quotation.quotation_number}' created by '{actor}' for company '{company.name}'.")
            return quotation
        except Exception as e:
            logger.error(f"Error creating SalesQuotation for company '{company.name}' by '{actor}': {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the sales quotation.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        validated_data.pop('company', None)  # prevent company change

        instance = super().update(instance, validated_data)
        actor = getattr(user, 'username', 'Unknown')
        logger.info(f"SalesQuotation '{instance.quotation_number}' updated by '{actor}'.")
        return instance
