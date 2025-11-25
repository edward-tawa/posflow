from rest_framework.viewsets import ReadOnlyModelViewSet
from branch.models.branch_model import Branch
from branch.serializers.branch_serializer import BranchSerializer
from branch.permissions.branch_permissions import BranchPermissions
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from config.utilities.pagination import StandardResultsSetPagination


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

