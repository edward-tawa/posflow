from rest_framework.viewsets import ReadOnlyModelViewSet
from branch.models.branch_model import Branch
from branch.serializers.branch_serializer import BranchSerializer
from branch.permissions.branch_permissions import BranchPermissions
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from config.utilities.pagination import StandardResultsSetPagination
from rest_framework.response import Response
from rest_framework import status
from loguru import logger
from company.models.company_model import Company
from users.models.user_model import User
from django.db import transaction

class BranchViewSet(ReadOnlyModelViewSet):
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
    
    def post(self, request):
        logger.info(request.data)
        try:
            logger.info(request.user.id)
            company_id = request.data.get("company")
            try:
                company = Company.objects.get(id=company_id)
                user_company = User.objects.get(id = request.user.id, company = company)
                with transaction.atomic():
                    branch = Branch.objects.create(
                        name=request.data.get("name"),
                        company=company,
                        code=request.data.get("code"),
                        address=request.data.get("address"),
                        city=request.data.get("city"),
                        country=request.data.get("country"),
                        phone_number=request.data.get("phone_number"),
                        manager_id=request.data.get("manager"),
                        is_active=request.data.get("is_active", True),
                        opening_date=request.data.get("opening_date"),
                        notes=request.data.get("notes"),
                    )

                return Response(
                    {"id": branch.id, "message": "Branch created successfully"},
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {'message': f'{e}'}
                )
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=404)

        except Exception as e:
            logger.error(str(e))
            return Response({"error": str(e)}, status=500)

