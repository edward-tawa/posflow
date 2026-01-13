from rest_framework import serializers
from currency.models.currency_model import Currency


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = [
            'id',
            'code',
            'name',
            'symbol',
            'is_base_currency',
            'exchange_rate_to_base',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_exchange_rate_to_base(self, value):
        if value <= 0:
            raise serializers.ValidationError("Exchange rate must be a positive number")
        return value

    def validate_code(self, value):
        if not value.isalpha() or len(value) > 10:
            raise serializers.ValidationError("Currency code must be alphabetic and max 10 characters")
        return value.upper()

    def validate_symbol(self, value):
        if not value:
            raise serializers.ValidationError("Currency symbol cannot be empty")
        return value

    def create(self, validated_data):
        # Optionally, you can handle base currency logic here if needed
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Prevent changing base currency accidentally; handle via service method
        validated_data.pop('is_base_currency', None)
        return super().update(instance, validated_data)
