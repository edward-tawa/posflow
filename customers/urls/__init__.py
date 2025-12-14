from .customer_urls import urlpatterns as customer_urlpatterns
from .customer_branch_history import urlpatterns as customer_branch_history_urlpatterns
from .create_cash_sale_urls import urlpatterns as create_cash_sale_urlpatterns
from .create_credit_sale_urls import urlpatterns as create_credit_sale_urlpatterns
from .customer_statement_urls import urlpatterns as customer_statement_urlpatterns
from .customer_credit_limit_urls import urlpatterns as customer_credit_limit_urlpatterns
from .customer_outstanding_balance_urls import urlpatterns as customer_outstanding_balance_urlpatterns
from .customer_refund_urls import urlpatterns as customer_refund_urlpatterns
urlpatterns = (
    customer_urlpatterns +
    customer_branch_history_urlpatterns+
    create_cash_sale_urlpatterns +
    create_credit_sale_urlpatterns +
    customer_statement_urlpatterns +
    customer_credit_limit_urlpatterns +
    customer_outstanding_balance_urlpatterns +
    customer_refund_urlpatterns
    )
