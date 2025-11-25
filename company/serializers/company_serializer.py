from rest_framework import serializers
from company.models.company_model import Company


class CompanySerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'email', 'password', 'website', 'logo', 
            'address', 'phone_number', 'is_active', 'is_staff', 
            'updated_at', 'created_at'
        ]
        read_only_fields = ['id', 'is_active', 'is_staff', 'updated_at', 'created_at']

    def create(self, validated_data):
        """Create a company and hash its password securely."""
        password = validated_data.pop('password')
        company = Company.objects.create_company(password=password, **validated_data)
        return company

    def update(self, instance, validated_data):
        """Update company details, allowing optional password change."""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
