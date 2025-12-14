from rest_framework import serializers


class AdjustStockSerializer(serializers.Serializer):
    adjustment = serializers.IntegerField(help_text="Positive to increase, negative to decrease stock")