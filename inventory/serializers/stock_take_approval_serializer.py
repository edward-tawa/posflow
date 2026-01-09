from rest_framework import serializers
from inventory.models.stock_take_approval_model import StockTakeApproval


class StockTakeApprovalSerializer(serializers.ModelSerializer):
    stock_take_summary = serializers.SerializerMethodField(read_only=True)
    approved_by_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = StockTakeApproval
        fields = [
            'id',
            'stock_take_summary',
            'approved_by_summary',
            'comment',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'stock_take_summary',
            'approved_by_summary',
            'created_at',
            'updated_at',
        ]

    def get_stock_take_summary(self, obj):
        return {
            'id': obj.stock_take.id,
            'reference': getattr(obj.stock_take, 'reference', None),
            'date': getattr(obj.stock_take, 'date', None),
        }

    def get_approved_by_summary(self, obj):
        return {
            'id': obj.approved_by.id,
            'email': obj.approved_by.email,
            'full_name': getattr(obj.approved_by, 'get_full_name', lambda: None)(),
        }

    def validate_comment(self, value):
        if value and len(value.strip()) < 3:
            raise serializers.ValidationError("Comment must be at least 3 characters long.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')

        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError("User information is missing in the request context")

        validated_data['approved_by'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Prevent changing approver or stock take after creation
        validated_data.pop('approved_by', None)
        validated_data.pop('stock_take', None)
        return super().update(instance, validated_data)
