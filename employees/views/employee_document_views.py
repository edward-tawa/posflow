from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from employees.models.employee_document_model import EmployeeDocument
from employees.serializers.employee_document_serializer import EmployeeDocumentSerializer
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from employees.permissions.employee_permissions import EmployeePermission
from config.pagination.pagination import StandardResultsSetPagination
from company.models.company_model import Company
from loguru import logger


class EmployeeDocumentViewSet(ModelViewSet):
    """
    ViewSet for viewing and managing employee documents.
    Supports listing, retrieving, creating (single/multiple), updating, and deleting documents.
    Includes detailed logging for key operations.
    """
    queryset = EmployeeDocument.objects.all()
    serializer_class = EmployeeDocumentSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [EmployeePermission]
    pagination_class = StandardResultsSetPagination
    parser_classes = [MultiPartParser, FormParser]  # required for file uploads

    # -------------------------
    # QUERYSET FILTERING
    # -------------------------
    def get_queryset(self):
        try:
            user = self.request.user
            if not user.is_authenticated:
                logger.warning("Unauthenticated access attempt to EmployeeDocumentViewSet.")
                return EmployeeDocument.objects.none()

            company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
            identifier = getattr(company, 'name', None) or getattr(user, 'username', None) or 'Unknown'

            if not company:
                logger.warning(f"{identifier} has no associated company.")
                return EmployeeDocument.objects.none()

            logger.info(f"{identifier} fetching employee documents for company '{getattr(company, 'name', 'Unknown')}'.")
            return EmployeeDocument.objects.filter(employee__company=company).select_related('employee')
        except Exception as e:
            logger.error(e)
            return self.queryset.none()

    # -------------------------
    # CREATE (single or multiple files)
    # -------------------------
    def create(self, request, *args, **kwargs):
        user = request.user
        files = request.FILES.getlist('documents')  # accept multiple files
        employee_id = request.data.get('employee')

        if not files:
            return Response({"detail": "No files provided."}, status=status.HTTP_400_BAD_REQUEST)

        created_docs = []
        for f in files:
            serializer = self.get_serializer(data={'employee': employee_id, 'document': f})
            serializer.is_valid(raise_exception=True)
            doc = serializer.save()
            created_docs.append(serializer.data)
            logger.info(
                f"Document '{doc['id']}' uploaded for employee '{employee_id}' by {user.username}."
            )

        return Response(created_docs, status=status.HTTP_201_CREATED)

    # -------------------------
    # UPDATE
    # -------------------------
    def perform_update(self, serializer):
        user = self.request.user
        document = serializer.save()
        logger.info(
            f"Document '{document.id}' for employee '{document.employee.id}' updated by {user.username}."
        )

    # -------------------------
    # DELETE
    # -------------------------
    def perform_destroy(self, instance):
        user = self.request.user
        logger.warning(
            f"Document '{instance.id}' for employee '{instance.employee.id}' deleted by {user.username}."
        )
        instance.delete()
