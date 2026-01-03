from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from branch.models.branch_model import Branch
from branch.serializers.branch_serializer import BranchSerializer
from branch.permissions.branch_permissions import BranchPermissions
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination_branch import StandardResultsSetPagination
from rest_framework.response import Response
from rest_framework import status
from loguru import logger
from company.models.company_model import Company
from users.models.user_model import User
from django.db import transaction
from rest_framework.exceptions import ValidationError


class BranchViewSet(ModelViewSet):
    """
    ViewSet for viewing Branches.
    - ReadOnlyModelViewSet: allows only GET requests.
    - Permissions: custom BranchPermissions.
    - Filtering: search and ordering.
    - Pagination: standard pagination.
    """
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [BranchPermissions]
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'city', 'country', 'manager__username']
    ordering_fields = ['name', 'city', 'country', 'opening_date']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'company'):
            return (
                self.queryset
                .filter(company=user.company)
                .select_related('company', 'manager')  # avoids extra queries
            )
        return self.queryset.none()

    def perform_create(self, serializer):
        user_company = None
        try:
            user_company = getattr(self.request.user, 'name')
        except Exception as e:
            user_company = getattr(self.request.user, 'company')
        logger.info(user_company)
        if not user_company:
            raise ValidationError({"error": "User has no associated company"})
        serializer.save()

    def perform_update(self, serializer):
        branch = self.get_object()
        user_company = getattr(self.request.user, 'company', None)

        if branch.company != user_company:
            raise ValidationError({"error": "You cannot update branches of another company"})
        
        serializer.save()

    def perform_destroy(self, instance):
        user_company = getattr(self.request.user, 'company', None)

        if instance.company != user_company:
            raise ValidationError({"error": "You cannot delete branches of another company"})

        instance.delete()
