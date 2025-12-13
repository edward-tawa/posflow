from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from payments.models.payment_receipt_item_model import PaymentReceiptItem
from payments.models.payment_receipt_model import PaymentReceipt
from users.models import User


class PaymentReceiptItemSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    payment_receipt_summary = serializers.SerializerMethodField(read_only=True)
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    tax_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = PaymentReceiptItem
        fields = [
            'id',
            'payment_receipt',
            'payment_receipt_summary',
            'company_summary',
            'branch_summary',
            'description',
            'quantity',
            'unit_price',
            'tax_rate',
            'subtotal',
            'tax_amount',
            'total_price',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'subtotal',
            'tax_amount',
            'total_price',
            'payment_receipt_summary',
            'created_at',
            'updated_at',
        ]

    def get_payment_receipt_summary(self, obj):
        receipt = obj.payment_receipt
        return {
            'id': receipt.id,
            'receipt_number': receipt.receipt_number,
            'amount': str(receipt.amount)
        }
    
    def get_company_summary(self, obj):
        receipt = obj.payment_receipt
        return {
            'id': receipt.company.id,
            'name': receipt.company.name,
        }
    
    def get_branch_summary(self, obj):
        receipt = obj.payment_receipt
        return {
            'id': receipt.branch.id,
            'name': receipt.branch.name,
        }

    def validate(self, attrs):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        payment_receipt = attrs.get('payment_receipt') or getattr(self.instance, 'payment_receipt', None)
        if payment_receipt and payment_receipt.company.id != expected_company.id:
            logger.error(f"{actor} attempted to create/update PaymentReceiptItem for company {payment_receipt.company.id}.")
            raise serializers.ValidationError(
                "You cannot create or update an item for a payment receipt outside your company."
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        payment_receipt = validated_data['payment_receipt']
        expected_company = get_expected_company(request)
        validated_data['payment_receipt'] = payment_receipt  # ensure correct receipt

        try:
            item = PaymentReceiptItem.objects.create(**validated_data)
            # Update receipt amount after creating item
            item.payment_receipt.update_amount_received()
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.info(f"PaymentReceiptItem '{item.description}' created for receipt '{payment_receipt.receipt_number}' by {actor}.")
            return item
        except Exception as e:
            logger.error(f"Error creating PaymentReceiptItem for receipt '{payment_receipt.receipt_number}' by {actor}: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the payment receipt item.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        expected_company = get_expected_company(request)

        # Prevent changing payment_receipt
        validated_data.pop('payment_receipt', None)

        if instance.payment_receipt.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to update PaymentReceiptItem '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot update an item outside your company.")

        instance = super().update(instance, validated_data)
        # Update receipt amount after item update
        instance.payment_receipt.update_amount_received()
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"PaymentReceiptItem '{instance.description}' updated for receipt '{instance.payment_receipt.receipt_number}' by {actor}.")
        return instance

    def delete(self):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        expected_company = get_expected_company(request)
        instance = self.instance

        if instance.payment_receipt.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to delete PaymentReceiptItem '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot delete an item outside your company.")

        # Update receipt amount after deletion
        instance.payment_receipt.update_amount_received()
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"PaymentReceiptItem '{instance.description}' deleted for receipt '{instance.payment_receipt.receipt_number}' by {actor}.")
        instance.delete()
