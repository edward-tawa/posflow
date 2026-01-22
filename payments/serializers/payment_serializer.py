from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from payments.models import Payment
from company.models.company_model import Company
from branch.models.branch_model import Branch
from users.models import User


class PaymentSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    paid_by_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'paid_by',
            'paid_by_summary',
            'payment_type',
            'payment_number',
            'payment_date',
            'currency',
            'total_amount',
            'status',
            'method',
            'reference_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'payment_number',
            'payment_date',
            'created_at',
            'updated_at',
            'company_summary',
            'paid_by_summary',
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

    def get_paid_by_summary(self, obj):
        if obj.paid_by:
            return {
                'id': obj.paid_by.id,
                'name': obj.paid_by.name
            }
        return None

    def validate(self, attrs):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if attrs.get('company') and attrs['company'].id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update Payment for company {attrs['company'].id}."
            )
            raise serializers.ValidationError(
                "You cannot create or update a payment for a company other than your own."
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
            payment = Payment.objects.create(**validated_data)
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.info(f"Payment '{payment.payment_number}' created for company '{expected_company.name}' by {actor}.")
            return payment
        except Exception as e:
            logger.error(f"Error creating Payment for company '{expected_company.name}' by {actor}: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the payment.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        # Prevent switching company or changing payment number
        validated_data.pop('company', None)
        validated_data.pop('payment_number', None)

        if instance.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to update Payment '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot update a payment outside your company.")

        instance = super().update(instance, validated_data)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"Payment '{instance.payment_number}' updated by {actor}.")
        return instance

    def delete(self):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        instance = self.instance

        if instance.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to delete Payment '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot delete a payment outside your company.")

        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"Payment '{instance.payment_number}' deleted by {actor}.")
        instance.delete()