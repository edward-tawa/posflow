from rest_framework import serializers
from sales.models.sales_receipt_model import SalesReceipt
from sales.models.sales_receipt_item_model import SalesReceiptItem
from company.models.company_model import Company
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger


class SalesReceiptSerializer(serializers.ModelSerializer):
    items = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SalesReceipt
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'sales_payment',
            'customer',
            'receipt_number',
            'receipt_date',
            'total_amount',
            'issued_by',
            'notes',
            'items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'company_summary', 'receipt_number', 'total_amount',
            'items', 'created_at', 'updated_at'
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
        company = attrs.get('company', expected_company)

        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if company.id != expected_company.id:
            logger.error(f"{actor} attempted to create/update SalesReceipt for company {company.id}.")
            raise serializers.ValidationError("You cannot create or update a sales receipt outside your company.")

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        company = get_expected_company(request)
        validated_data['company'] = company

        try:
            receipt = SalesReceipt.objects.create(**validated_data)
            actor = getattr(user, 'username', 'Unknown')
            logger.info(f"SalesReceipt '{receipt.receipt_number}' created by '{actor}' for company '{company.name}'.")
            return receipt
        except Exception as e:
            logger.error(f"Error creating SalesReceipt for company '{company.name}' by '{actor}': {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the sales receipt.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        validated_data.pop('company', None)  # Prevent company switch

        instance = super().update(instance, validated_data)
        actor = getattr(user, 'username', 'Unknown')
        logger.info(f"SalesReceipt '{instance.receipt_number}' updated by '{actor}'.")
        return instance
