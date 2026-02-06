from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from payments.models.payment_plan_model import PaymentPlan



class PaymentPlanSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    payment_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PaymentPlan
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'payment',
            'payment_summary',
            'name',
            'requires_deposit',
            'deposit_percentage',
            'max_duration_days',
            'valid_from',
            'valid_until',
            'reference_number',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'company_summary',
            'branch_summary',
            'payment_summary',
            'reference_number',
            'created_at',
            'updated_at',
        ]

    # ------------------------
    # Summary helpers
    # ------------------------
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

    def get_payment_summary(self, obj):
        return {
            'id': obj.payment.id,
            'amount': getattr(obj.payment, 'amount', None)
        }

    # ------------------------
    # Validation
    # ------------------------
    def validate(self, attrs):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        payment = attrs.get('payment')
        if payment and payment.company_id != expected_company.id:
            logger.error(f"{actor} attempted to link PaymentPlan to foreign Payment.")
            raise serializers.ValidationError(
                "Payment does not belong to your company."
            )

        return attrs

    # ------------------------
    # Create
    # ------------------------
    def create(self, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        # Enforce company/branch
        validated_data['company'] = expected_company
        validated_data['branch'] = request.user.branch

        try:
            payment_plan = PaymentPlan.objects.create(**validated_data)
            logger.info(
                f"PaymentPlan '{payment_plan.reference_number}' created for company "
                f"'{expected_company.name}' by {actor}."
            )
            return payment_plan

        except Exception as e:
            logger.error(
                f"Error creating PaymentPlan for company '{expected_company.name}' by {actor}: {str(e)}"
            )
            raise serializers.ValidationError(
                "An error occurred while creating the payment plan."
            )

    # ------------------------
    # Update
    # ------------------------
    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        # Block immutable / enforced fields
        validated_data.pop('company', None)
        validated_data.pop('branch', None)
        validated_data.pop('reference_number', None)

        if instance.company.id != expected_company.id:
            logger.warning(
                f"{actor} attempted to update PaymentPlan '{instance.id}' outside their company."
            )
            raise serializers.ValidationError(
                "You cannot update a payment plan outside your company."
            )

        instance = super().update(instance, validated_data)
        logger.info(f"PaymentPlan '{instance.reference_number}' updated by {actor}.")
        return instance

    # ------------------------
    # Delete
    # ------------------------
    def delete(self):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        instance = self.instance
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if instance.company.id != expected_company.id:
            logger.warning(
                f"{actor} attempted to delete PaymentPlan '{instance.reference_number}' outside their company."
            )
            raise serializers.ValidationError(
                "You cannot delete a payment plan outside your company."
            )

        logger.info(f"PaymentPlan '{instance.reference_number}' deleted by {actor}.")
        instance.delete()
