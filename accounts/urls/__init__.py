from .account_urls import urlpatterns as account_urls
from .branch_accounts_urls import urlpatterns as branch_account_urls
from .customer_account_urls import urlpatterns as customer_account_urls
from .employee_account_urls import urlpatterns as employee_account_urls
from .loan_account_urls import urlpatterns as loan_account_urls
from .supplier_account_urls import urlpatterns as supplier_account_urls



urlpatterns = branch_account_urls + customer_account_urls + employee_account_urls + loan_account_urls + supplier_account_urls + account_urls