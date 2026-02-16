from .employee_urls import urlpatterns as employee_urlpatterns
from .remuneration_urls import urlpatterns as remuneration_urlpatterns
from .employee_document_urls import urlpatterns as employee_document_urlpatterns
from .employee_contract_urls import urlpatterns as employee_contract_urlpatterns
from .employee_budget_urls import urlpatterns as employee_budget_urlpatterns
from .employee_attendance_urls import urlpatterns as employee_attendance_urlpatterns


url_patterns = (
    employee_urlpatterns + 
    remuneration_urlpatterns + 
    employee_document_urlpatterns + 
    employee_contract_urlpatterns +     
    employee_budget_urlpatterns +
    employee_attendance_urlpatterns
)  


