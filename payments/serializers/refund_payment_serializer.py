from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from payments.models.refund_payment_model import RefundPayment
from payments.models.refund_model import Refund
from users.models import User


class RefundPaymentSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    # Summary fields
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    processed_by_summary = serializers.SerializerMethodField(read_only=True)
    refund_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RefundPayment
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'payment',
            'payment_method',
            'refund',
            'refund_summary',
            'processed_by',
            'processed_by_summary',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'company_summary',
            'branch_summary',
            'refund_summary',
            'processed_by_summary',
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

    def get_processed_by_summary(self, obj):
        if obj.processed_by:
            return {
                'id': obj.processed_by.id,
                'name': obj.processed_by.name
            }
        return None

    def get_refund_summary(self, obj):
        return {
            'id': obj.refund.id,
            'refund_number': getattr(obj.refund, 'refund_number', None),
            'total_amount': getattr(obj.refund, 'total_amount', None)
        }

    # ------------------------
    # Validation
    # ------------------------

    def validate(self, attrs):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        refund = attrs.get('refund')
        if refund and refund.company_id != expected_company.id:
            logger.error(f"{actor} attempted to link RefundPayment to foreign Refund.")
            raise serializers.ValidationError(
                "Refund does not belong to your company."
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

        # Enforce ownership
        validated_data['company'] = expected_company
        validated_data['branch'] = request.user.branch
        validated_data['processed_by'] = user

        try:
            refund_payment = RefundPayment.objects.create(**validated_data)
            logger.info(
                f"RefundPayment '{refund_payment.id}' created for company "
                f"'{expected_company.name}' by {actor}."
            )
            return refund_payment

        except Exception as e:
            logger.error(
                f"Error creating RefundPayment for company "
                f"'{expected_company.name}' by {actor}: {str(e)}"
            )
            raise serializers.ValidationError(
                "An error occurred while creating the refund payment."
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
        validated_data.pop('processed_by', None)
        validated_data.pop('refund', None)

        if instance.company.id != expected_company.id:
            logger.warning(
                f"{actor} attempted to update RefundPayment '{instance.id}' outside their company."
            )
            raise serializers.ValidationError(
                "You cannot update a refund payment outside your company."
            )

        instance = super().update(instance, validated_data)

        logger.info(
            f"RefundPayment '{instance.id}' updated by {actor}."
        )
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
                f"{actor} attempted to delete RefundPayment '{instance.id}' outside their company."
            )
            raise serializers.ValidationError(
                "You cannot delete a refund payment outside your company."
            )

        logger.info(
            f"RefundPayment '{instance.id}' deleted by {actor}."
        )
        instance.delete()
