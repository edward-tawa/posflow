from rest_framework import serializers
from users.models.user_model import User
from users.serializers.company_field import CompanyRelatedField

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    company = CompanyRelatedField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'company', 'role', 'password', 
            'is_active', 'is_staff', 'updated_at', 'created_at'
        ]
        read_only_fields = ['id', 'is_active', 'updated_at', 'created_at']

    def create(self, validated_data):
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
