from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from company.models.company_model import Company
from suppliers.models.supplier_model import Supplier
from users.models import User
from suppliers.models.supplier_debit_note_model import SupplierDebitNote


class SupplierDebitNoteSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        required=True
    )

    class Meta:
        model = SupplierDebitNote
        fields = [
            'id',
            'company',
            'company_summary',
            'supplier',
            'debit_note_number',
            'debit_date',
            'issued_by',
            'total_amount',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'debit_note_number', 'debit_date']

    def get_company_summary(self, obj):
        return {
            'id': obj.company.id,
            'name': obj.company.name
        }

    def validate(self, attrs):
        """Validate total_amount within company context"""
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if attrs.get('company') and attrs['company'].id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update SupplierDebitNote for company {attrs['company'].id}."
            )
            raise serializers.ValidationError(
                "You cannot create or update a debit note for a company other than your own."
            )

        # Validate total_amount
        total_amount = attrs.get('total_amount')
        if total_amount is not None and total_amount <= 0:
            raise serializers.ValidationError("Total amount must be greater than zero.")

        return attrs

    def create(self, validated_data):
        """Create a new SupplierDebitNote with logging and company enforcement"""
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        validated_data['company'] = expected_company  # Force company

        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        supplier = validated_data.get('supplier')

        try:
            logger.info(validated_data)
            debit_note = SupplierDebitNote.objects.create(**validated_data)
            logger.info(
                f"SupplierDebitNote '{debit_note.debit_note_number}' for supplier '{supplier.name}' "
                f"created for company '{expected_company.name}' by {actor}."
            )
            return debit_note
        except Exception as e:
            logger.error(
                f"Error creating SupplierDebitNote for supplier '{supplier.name}' "
                f"for company '{expected_company.name}' by {actor}: {str(e)}"
            )
            raise serializers.ValidationError("An error occurred while creating the debit note.")

    def update(self, instance, validated_data):
        """Update an existing SupplierDebitNote with company validation and logging"""
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        # Prevent changes to company and debit_note_number
        validated_data.pop('company', None)
        validated_data.pop('debit_note_number', None)

        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if instance.company != expected_company:
            logger.warning(
                f"{actor} attempted to update SupplierDebitNote {instance.id} outside their company."
            )
            raise serializers.ValidationError("You cannot update a debit note outside your company.")

        instance = super().update(instance, validated_data)
        logger.info(
            f"SupplierDebitNote '{instance.debit_note_number}' updated by '{actor}'."
        )
        return instance
