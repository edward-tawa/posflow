from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from payments.models.payment_plan_model import PaymentPlan
from payments.serializers.payment_plan_serializer import PaymentPlanSerializer
from payments.permissions.payment_permissions import PaymentsPermissions
from loguru import logger


class PaymentPlanViewSet(ModelViewSet):
    """
    ViewSet for managing PaymentPlans.
    Supports listing, retrieving, creating, updating, and deleting payment plans.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = PaymentPlan.objects.all()
    serializer_class = PaymentPlanSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [PaymentsPermissions]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'id',
        'company__name',
        'branch__name',
        'payment__reference_number',
        'reference_number',
        'name'
    ]
    ordering_fields = ['created_at', 'updated_at', 'id', 'valid_from', 'valid_until']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            return get_company_queryset(self.request, PaymentPlan).select_related(
                'company', 'branch', 'payment'
            )
        except Exception as e:
            logger.error(f"Error fetching PaymentPlan queryset: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        payment_plan = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.success(
            f"PaymentPlan '{payment_plan.reference_number}' created by '{actor}' "
            f"for company '{payment_plan.company.name}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        payment_plan = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.info(
            f"PaymentPlan '{payment_plan.reference_number}' updated by '{actor}' "
            f"for company '{payment_plan.company.name}'."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = get_logged_in_company(self.request)

        reference_number = instance.reference_number
        instance.delete()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.warning(
            f"PaymentPlan '{reference_number}' deleted by '{actor}' "
            f"from company '{company.name}'."
        )
