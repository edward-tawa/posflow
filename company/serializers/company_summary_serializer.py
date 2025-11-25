from rest_framework import serializers
from company.models.company_model import Company

class CompanySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name']  # only what you need
