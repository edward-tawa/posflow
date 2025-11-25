from rest_framework import serializers
from branch.models.branch_model import Branch
from company.serializers.company_serializer import CompanySerializer



class BranchSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    class Meta:
        model = Branch
        fields = [
            'id',
            'name',
            'company',
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
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None
        validated_data['company'] = user.company if user and hasattr(user, 'company') else None
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Prevent changing the company on update
        validated_data.pop('company', None)
        return super().update(instance, validated_data)