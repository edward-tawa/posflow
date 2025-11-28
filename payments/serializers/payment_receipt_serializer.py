from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from payments.models import PaymentReceipt, Payment
from company.models.company_model import Company
from branch.models.branch_model import Branch
from users.models import User


class PaymentReceiptSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    payment_summary = serializers.SerializerMethodField(read_only=True)
    issued_by_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PaymentReceipt
        fields = [
            'id',
            'company',
            'company_summary',
            'branch',
            'branch_summary',
            'payment',
            'payment_summary',
            'receipt_number',
            'receipt_date',
            'amount',
            'issued_by',
            'issued_by_summary',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'receipt_number',
            'receipt_date',
            'created_at',
            'updated_at',
            'company_summary',
            'branch_summary',
            'payment_summary',
            'issued_by_summary',
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

    def get_payment_summary(self, obj):
        return {
            'id': obj.payment.id,
            'payment_number': obj.payment.payment_number,
            'amount': str(obj.payment.amount),
        }

    def get_issued_by_summary(self, obj):
        if obj.issued_by:
            return {
                'id': obj.issued_by.id,
                'name': obj.issued_by.name
            }
        return None

    def validate(self, attrs):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if attrs.get('company') and attrs['company'].id != expected_company.id:
            logger.error(f"{actor} attempted to create/update PaymentReceipt for company {attrs['company'].id}.")
            raise serializers.ValidationError(
                "You cannot create or update a payment receipt for a company other than your own."
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        validated_data['company'] = expected_company  # enforce company

        try:
            receipt = PaymentReceipt.objects.create(**validated_data)
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.info(f"PaymentReceipt '{receipt.receipt_number}' created for company '{expected_company.name}' by {actor}.")
            return receipt
        except Exception as e:
            logger.error(f"Error creating PaymentReceipt for company '{expected_company.name}' by {actor}: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the payment receipt.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        # Prevent changing company or receipt_number
        validated_data.pop('company', None)
        validated_data.pop('receipt_number', None)

        if instance.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to update PaymentReceipt '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot update a payment receipt outside your company.")

        instance = super().update(instance, validated_data)
        # After update, recalc amount
        instance.update_amount_received()
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"PaymentReceipt '{instance.receipt_number}' updated by {actor}.")
        return instance

    def delete(self):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        instance = self.instance

        if instance.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to delete PaymentReceipt '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot delete a payment receipt outside your company.")

        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"PaymentReceipt '{instance.receipt_number}' deleted by {actor}.")
        instance.delete()
