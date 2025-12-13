from rest_framework import serializers
from company.models.company_model import Company
from suppliers.models.supplier_model import Supplier
from company.serializers.company_serializer import CompanySerializer
from branch.models.branch_model import Branch
from company.serializers.company_summary_serializer import CompanySummarySerializer
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger


class SupplierSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = CompanySummarySerializer(source='company', read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
   
    class Meta:
        model = Supplier
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'name',
            'email',
            'phone_number',
            'address',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    #Missing link to branch
    def get_branch_summary(self, obj):
        return {
            None
        }

    def validate(self, attrs):
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, "user", None)

        # Determine actor for logging
        actor = getattr(user, "username", None) or getattr(expected_company, "name", "Unknown")

        if attrs['company'].id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update Supplier "
                f"for company {attrs['company'].id}."
            )
            raise serializers.ValidationError(
                "You cannot create or update a supplier for a company other than your own."
            )

        return attrs


    def create(self, validated_data):
        """
        CREATE()
        ---------------------
        Create a new Supplier instance after validating the company context.
        ---------------------
        """
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, "user", None)
        validated_data['company'] = expected_company  # Force company

        # Determine actor for logging
        actor = getattr(user, "username", None) or getattr(expected_company, "name", "Unknown")

        try:
            supplier = Supplier.objects.create(**validated_data)
            logger.info(
                f"Supplier '{supplier.name}' created for company '{expected_company.name}' "
                f"by {actor}."
            )
            return supplier
        except Exception as e:
            logger.error(
                f"Error creating Supplier for company '{expected_company.name}' by {actor}: {str(e)}"
            )
            raise serializers.ValidationError("An error occurred while creating the supplier.")


    def update(self, instance, validated_data):
        """
        UPDATE()
        ---------------------
        Update an existing Supplier instance after validating the company context.
        ---------------------
        """
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, "user", None)
        validated_data.pop('company', None)  # Prevent company switch

        # Determine actor for logging
        actor = getattr(user, "username", None) or getattr(expected_company, "name", "Unknown")

        if instance.company != expected_company:
            logger.warning(
                f"{actor} attempted to update Supplier {instance.id} outside their company."
            )
            raise serializers.ValidationError("You cannot update a supplier outside your company.")

        return super().update(instance, validated_data)
