from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from suppliers.models.supplier_debit_note_model import SupplierDebitNote
from suppliers.models.supplier_debit_note_item_model import SupplierDebitNoteItem
from company.models.company_model import Company
from users.models import User
from suppliers.models.supplier_model import Supplier



class SupplierDebitNoteItemSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    supplier_debit_note_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SupplierDebitNoteItem
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'supplier_debit_note',
            'supplier_debit_note_summary',
            'description',
            'quantity',
            'unit_price',
            'total_price',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_price']

    def get_supplier_debit_note_summary(self, obj):
        note = obj.supplier_debit_note
        return {
            'id': note.id,
            'debit_note_number': note.debit_note_number,
            'supplier_id': note.supplier.id,
            'supplier_name': note.supplier.name,
        }
    
    def get_company_summary(self, obj):
        return {
            'id': obj.supplier_debit_note.company.id,
            'name': obj.supplier_debit_note.company.name,
        }

    #Missing link to branch
    def get_branch_summary(self, obj):
        return {
            None
        }


    def validate(self, attrs):
        """Validate quantity and unit_price"""
        if attrs.get('quantity') is not None and attrs['quantity'] <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")

        if attrs.get('unit_price') is not None and attrs['unit_price'] <= 0:
            raise serializers.ValidationError("Unit price must be greater than zero.")

        return attrs

    def create(self, validated_data):
        """Create a new SupplierDebitNoteItem with logging"""
        note = validated_data.get('supplier_debit_note')
        actor = getattr(self.context['request'].user, 'username', 'Unknown')
        try:
            item = SupplierDebitNoteItem.objects.create(**validated_data)
            logger.info(
                f"SupplierDebitNoteItem {item.id} for debit note {note.debit_note_number} "
                f"created by {actor}."
            )
            return item
        except Exception as e:
            logger.error(
                f"Error creating SupplierDebitNoteItem for debit note {note.debit_note_number} "
                f"by {actor}: {str(e)}"
            )
            raise serializers.ValidationError("An error occurred while creating the debit note item.")

    def update(self, instance, validated_data):
        """Update an existing SupplierDebitNoteItem with logging"""
        note = instance.supplier_debit_note
        actor = getattr(self.context['request'].user, 'username', 'Unknown')
        instance = super().update(instance, validated_data)
        logger.info(
            f"SupplierDebitNoteItem {instance.id} for debit note {note.debit_note_number} "
            f"updated by {actor}."
        )
        return instance
