from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from employees.models.employee_model import Employee
from employees.models.employee_document_model import EmployeeDocument
from company.models.company_model import Company
from branch.models.branch_model import Branch
from users.models.user_model import User


class EmployeeDocumentSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    employee_summary = serializers.SerializerMethodField(read_only=True)
    uploaded_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = EmployeeDocument
        fields = [
            'id',
            'employee_summary',
            'document',
            'uploaded_at',
        ]
        read_only_fields = [
            'id',
            'uploaded_at',
        ]

    # -------------------------
    # SUMMARY FIELDS
    # -------------------------
    def get_employee_summary(self, obj):
        return {
            'id': obj.employee.id,
            'full_name': f"{obj.employee.first_name} {obj.employee.last_name}",
            'email': obj.employee.email
        }

    # -------------------------
    # VALIDATION
    # -------------------------
    def validate(self, attrs):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        expected_company = get_expected_company(request)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        employee = attrs.get('employee')
        if employee and employee.company.id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update a document for employee {employee.id} "
                f"outside their company {expected_company.id}."
            )
            raise serializers.ValidationError(
                "You cannot upload a document for an employee outside your company."
            )

        document = attrs.get('document')
        if document is None:
            raise serializers.ValidationError({"document": "No file provided."})

        return attrs

    # -------------------------
    # CREATE
    # -------------------------
    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or 'Unknown'

        try:
            document = EmployeeDocument.objects.create(**validated_data)
            logger.info(
                f"Document '{document.id}' uploaded for employee '{document.employee.id}' "
                f"by {actor}."
            )
            return document
        except Exception as e:
            logger.error(
                f"Error uploading document for employee '{validated_data.get('employee').id}' by {actor}: {str(e)}"
            )
            raise serializers.ValidationError(
                "An error occurred while uploading the document."
            )

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or 'Unknown'

        instance = super().update(instance, validated_data)
        logger.info(
            f"Document '{instance.id}' for employee '{instance.employee.id}' updated by {actor}."
        )
        return instance
