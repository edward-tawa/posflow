from .account_urls import urlpatterns as account_urls
from .branch_accounts_urls import urlpatterns as branch_account_urls
from .customer_account_urls import urlpatterns as customer_account_urls
from .employee_account_urls import urlpatterns as employee_account_urls
from .loan_account_urls import urlpatterns as loan_account_urls
from .supplier_account_urls import urlpatterns as supplier_account_urls
from .bank_account_urls import urlpatterns as bank_account_urls
from .cash_account_urls import urlpatterns as cash_account_urls 
from .sales_account_urls import urlpatterns as sales_account_urls
from .purchases_account_urls import urlpatterns as purchases_account_urls
from .sales_returns_account_urls import urlpatterns as sales_returns_account_urls
from .purchases_returns_account_urls import urlpatterns as purchases_returns_account_urls
from .expense_account_ursl import urlpatterns as expense_account_urls



urlpatterns = (
        branch_account_urls +
                customer_account_urls +
                  employee_account_urls + 
                  loan_account_urls +
                     supplier_account_urls +
                       account_urls +
                         bank_account_urls +
                           cash_account_urls +
                             sales_account_urls +
                               purchases_account_urls + 
                               sales_returns_account_urls +
                                 purchases_returns_account_urls +
                                   expense_account_urls
                                   )