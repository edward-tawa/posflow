from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from payments.models.sales_payment_model import SalesPayment
from company.models.company_model import Company
from branch.models.branch_model import Branch
from users.models import User


class SalesPaymentSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    # Summary fields
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    received_by_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SalesPayment
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'sales_order',
            'sales_invoice',
            'payment',
            'payment_method',
            'received_by',
            'received_by_summary',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'company_summary',
            'branch_summary',
            'received_by_summary',
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

    def get_received_by_summary(self, obj):
        if obj.received_by:
            return {
                'id': obj.received_by.id,
                'name': obj.received_by.name
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

        # Ensure sales_order or sales_invoice belongs to same company
        sales_order = attrs.get('sales_order')
        sales_invoice = attrs.get('sales_invoice')

        if sales_order and sales_order.company_id != expected_company.id:
            logger.error(f"{actor} attempted to link SalesPayment to чуж SalesOrder.")
            raise serializers.ValidationError(
                "Sales order does not belong to your company."
            )

        if sales_invoice and sales_invoice.company_id != expected_company.id:
            logger.error(f"{actor} attempted to link SalesPayment to чуж SalesInvoice.")
            raise serializers.ValidationError(
                "Sales invoice does not belong to your company."
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
        validated_data['received_by'] = user

        try:
            sales_payment = SalesPayment.objects.create(**validated_data)
            logger.info(
                f"SalesPayment '{sales_payment.id}' created for company"
                f"'{expected_company.name}' by {actor}."
            )
            return sales_payment

        except Exception as e:
            logger.error(
                f"Error creating SalesPayment for company "
                f"'{expected_company.name}' by {actor}: {str(e)}"
            )
            raise serializers.ValidationError(
                "An error occurred while creating the sales payment."
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
        validated_data.pop('received_by', None)

        if instance.company.id != expected_company.id:
            logger.warning(
                f"{actor} attempted to update SalesPayment '{instance.id}' outside their company."
            )
            raise serializers.ValidationError(
                "You cannot update a sales payment outside your company."
            )

        instance = super().update(instance, validated_data)

        logger.info(
            f"SalesPayment '{instance.id}' updated by {actor}."
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
                f"{actor} attempted to delete SalesPayment '{instance.id}' outside their company."
            )
            raise serializers.ValidationError(
                "You cannot delete a sales payment outside your company."
            )

        logger.info(
            f"SalesPayment '{instance.id}' deleted by {actor}."
        )
        instance.delete()
