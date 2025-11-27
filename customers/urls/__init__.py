from .customer_urls import urlpatterns as customer_urlpatterns
from .customer_branch_history import urlpatterns as customer_branch_history_urlpatterns

urlpatterns = []
url_patterns = customer_urlpatterns + customer_branch_history_urlpatterns
