from .employee_urls import urlpatterns as employee_urlpatterns
from .remuneration_urls import urlpatterns as remuneration_urlpatterns
from .employee_document_urls import urlpatterns as employee_document_urlpatterns

url_patterns = (
    employee_urlpatterns + 
    remuneration_urlpatterns + 
    employee_document_urlpatterns 
)