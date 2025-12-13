from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from transactions.models import TransactionItem, Transaction
from inventory.models import Product
from company.models.company_model import Company


class TransactionItemSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    transaction_number = serializers.CharField(source='transaction.transaction_number', read_only=True)
    transaction_company_summary = serializers.SerializerMethodField(read_only=True)
    transaction_branch_summary = serializers.SerializerMethodField(read_only=True)
    product_name = serializers.CharField(read_only=True)  # optional if stored
    transaction = serializers.PrimaryKeyRelatedField(queryset=Transaction.objects.all(), required=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=True)
 
    class Meta:
        model = TransactionItem
        fields = [
            'id',
            'transaction',
            'transaction_number',
            'transaction_company_summary',
            'transaction_branch_summary',
            'product',
            'product_name',
            'quantity',
            'unit_price',
            'tax_rate',
            'subtotal',
            'tax_amount',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'transaction_number',
            'transaction_company_summary',
            'product_name',
            'subtotal',
            'tax_amount',
            'created_at',
            'updated_at',
        ]

    def get_transaction_company_summary(self, obj):
        company = obj.transaction.company
        return {
            'id': company.id,
            'name': company.name
        }
    
    def get_transaction_branch_summary(self, obj):
        branch = obj.transaction.branch
        return {
            'id': branch.id,
            'name': branch.name
        }

    def validate(self, attrs):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        transaction = attrs.get('transaction') or getattr(self.instance, 'transaction', None)
        if transaction and transaction.company.id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update TransactionItem for transaction '{transaction.id}' outside their company."
            )
            raise serializers.ValidationError(
                "You cannot create or update a transaction item for a transaction outside your company."
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        logger.info(validated_data)
        transaction = validated_data.get('transaction')
        validated_data['product_name'] = validated_data['product'].name  # store snapshot
        actor = None
        try:
            item = TransactionItem.objects.create(**validated_data)
            # update transaction total
            item.transaction.update_total_amount()
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.info(f"TransactionItem '{item.id}' created for transaction '{transaction.transaction_number}' by {actor}.")
            return item
        except Exception as e:
            logger.error(f"Error creating TransactionItem for transaction '{transaction.transaction_number}' by {actor}: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the transaction item.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        validated_data.pop('transaction', None)  # prevent switching transaction
        validated_data.pop('product_name', None)  # prevent changing product snapshot

        if instance.transaction.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to update TransactionItem '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot update a transaction item outside your company.")

        instance = super().update(instance, validated_data)
        # update transaction total
        instance.transaction.update_total_amount()
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"TransactionItem '{instance.id}' updated for transaction '{instance.transaction.transaction_number}' by {actor}.")
        return instance
