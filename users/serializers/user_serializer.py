from rest_framework import serializers
from users.models.user_model import User
from users.serializers.company_field import CompanyRelatedField
from branch.models.branch_model import Branch
from company.models.company_model import Company
from django.db.models import Q
from loguru import logger

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    company = CompanyRelatedField(required=False, allow_null=True)
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email', 
            'first_name', 
            'last_name', 
            'company',
            'company_summary',
            'branch_summary',
            'role', 
            'employment_type',
            'department',
            'photo',
            'password', 
            'is_active', 
            'is_staff', 
            'updated_at', 
            'created_at', 
            'username',
            'branch'
        ]
        read_only_fields = ['id', 'is_active', 'updated_at', 'created_at']

    def get_company_summary(self, obj):
        return{
            "id": obj.company.id,
            "name": obj.company.name
        }
    
    def get_branch_summary(self, obj):
        return{
            "id": obj.branch.id if obj.branch else None,
            "name": obj.branch.name if obj.branch else None
        }
    
    def create(self, validated_data):
        request = self.context.get('request')
        company_data = None
        try:
            company_data = Company.objects.get(name = request.user.name)
        except Exception as e:
            logger.error(e)
            return f'Error: {e}'
        validated_data['company'] = company_data
        password = validated_data.pop('password')
        # Pop is_staff if provided, default to False
        is_staff = validated_data.pop('is_staff', False)
        
        user = User.objects.create_user(password=password, is_staff=is_staff, **validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
