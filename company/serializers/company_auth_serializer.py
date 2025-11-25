# company/serializers/company_auth_serializer.py
from rest_framework import serializers

class CompanyLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
