from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from sales.models.delivery_note_model import DeliveryNote
from company.models.company_model import Company
from branch.models.branch_model import Branch
from customers.models.customer_model import Customer
from sales.models.sales_order_model import SalesOrder
from users.models import User


class DeliveryNoteSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=True)

    class Meta:
        model = DeliveryNote
        fields = [
            'id',
            'company',
            'company_summary',
            'branch',
            'customer',
            'sales_order',
            'delivery_number',
            'delivery_date',
            'total_amount',
            'issued_by',
            'tax_rate',
            # 'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'delivery_number', 'total_amount'
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
                f"{actor} attempted to create/update DeliveryNote for company {attrs['company'].id}."
            )
            raise serializers.ValidationError(
                "You cannot create or update a delivery note for a company other than your own."
            )

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        validated_data['company'] = expected_company  # enforce company

        try:
            delivery_note = DeliveryNote.objects.create(**validated_data)
            actor = getattr(user, 'username', 'Unknown')
            logger.info(
                f"DeliveryNote '{delivery_note.delivery_number}' created for company '{expected_company.name}' by {actor}."
            )
            return delivery_note
        except Exception as e:
            logger.error(
                f"Error creating DeliveryNote for company '{expected_company.name}' by {actor}: {str(e)}"
            )
            raise serializers.ValidationError("An error occurred while creating the delivery note.")

    def update(self, instance, validated_data):
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        # Prevent changing the company or delivery_number
        validated_data.pop('company', None)
        validated_data.pop('delivery_number', None)

        if instance.company.id != expected_company.id:
            actor = getattr(user, 'username', 'Unknown')
            logger.warning(
                f"{actor} attempted to update DeliveryNote '{instance.id}' outside their company."
            )
            raise serializers.ValidationError(
                "You cannot update a delivery note outside your company."
            )

        instance = super().update(instance, validated_data)
        actor = getattr(user, 'username', 'Unknown')
        logger.info(
            f"DeliveryNote '{instance.delivery_number}' updated by {actor} in company '{expected_company.name}'."
        )
        return instance
