from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from payments.models.purchase_payment_model import PurchasePayment
from company.models.company_model import Company
from branch.models.branch_model import Branch
from users.models import User


class PurchasePaymentSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    # Summary fields
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    issued_by_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PurchasePayment
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'payment',
            'payment_method',
            'purchase_order',
            'purchase',
            'purchase_invoice',
            'issued_by',
            'issued_by_summary',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'company_summary',
            'branch_summary',
            'issued_by_summary',
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

    def get_issued_by_summary(self, obj):
        if obj.issued_by:
            return {
                'id': obj.issued_by.id,
                'name': obj.issued_by.name
            }
        return None

    # ------------------------
    # Validation
    # ------------------------

    def validate(self, attrs):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        purchase_order = attrs.get('purchase_order')
        purchase = attrs.get('purchase')
        purchase_invoice = attrs.get('purchase_invoice')

        if purchase_order and purchase_order.company_id != expected_company.id:
            logger.error(f"{actor} attempted to link PurchasePayment to foreign PurchaseOrder.")
            raise serializers.ValidationError(
                "Purchase order does not belong to your company."
            )

        if purchase and purchase.company_id != expected_company.id:
            logger.error(f"{actor} attempted to link PurchasePayment to foreign Purchase.")
            raise serializers.ValidationError(
                "Purchase does not belong to your company."
            )

        if purchase_invoice and purchase_invoice.company_id != expected_company.id:
            logger.error(f"{actor} attempted to link PurchasePayment to foreign PurchaseInvoice.")
            raise serializers.ValidationError(
                "Purchase invoice does not belong to your company."
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
        validated_data['issued_by'] = user

        try:
            purchase_payment = PurchasePayment.objects.create(**validated_data)
            logger.info(
                f"PurchasePayment '{purchase_payment.id}' created for company "
                f"'{expected_company.name}' by {actor}."
            )
            return purchase_payment

        except Exception as e:
            logger.error(
                f"Error creating PurchasePayment for company "
                f"'{expected_company.name}' by {actor}: {str(e)}"
            )
            raise serializers.ValidationError(
                "An error occurred while creating the purchase payment."
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
        validated_data.pop('issued_by', None)

        if instance.company.id != expected_company.id:
            logger.warning(
                f"{actor} attempted to update PurchasePayment '{instance.id}' outside their company."
            )
            raise serializers.ValidationError(
                "You cannot update a purchase payment outside your company."
            )

        instance = super().update(instance, validated_data)

        logger.info(
            f"PurchasePayment '{instance.id}' updated by {actor}."
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
                f"{actor} attempted to delete PurchasePayment '{instance.id}' outside their company."
            )
            raise serializers.ValidationError(
                "You cannot delete a purchase payment outside your company."
            )

        logger.info(
            f"PurchasePayment '{instance.id}' deleted by {actor}."
        )
        instance.delete()
