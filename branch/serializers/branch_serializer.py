from rest_framework import serializers
from branch.models.branch_model import Branch
from company.serializers.company_serializer import CompanySerializer
from company.models.company_model import Company
from django.db.models import Q
from loguru import logger


class BranchSerializer(serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Branch
        fields = [
            'id',
            'name',
            'company_summary',
            'code',
            'address',
            'city',
            'country',
            'phone_number',
            'manager',
            'is_active',
            'opening_date',
            'notes',
            'full_address',
        ]
        read_only_fields = ['id', 'full_address']

    def get_company_summary(self, obj):
        return {
            "id": obj.company.id,
            "name": obj.company.name
        }
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None
        validated_data['company'] = None
        try:
            if user.role in ['Admin', 'Manager']:
                validated_data['company'] = Company.objects.get(Q(id = user.company.id) | Q(name = user.company.name))
        except Exception as e:
            validated_data['company'] = Company.objects.get(name = user.name)
            logger.info(validated_data)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Prevent changing the company on update
        validated_data.pop('company', None)
        return super().update(instance, validated_data)