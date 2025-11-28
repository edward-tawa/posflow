"""
URL configuration for posflow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    # Company app endpoints
    path('posflow/', include('company.urls')),

    # Users app endpoints
    path('posflow/', include('users.urls')),
    
    # Branch app endpoints
    path('posflow/', include('branch.urls')),

    # Account app endpoints
    path('posflow/', include('accounts.urls')),

    # Customers app endpoints
    path('posflow/', include('customers.urls')),

    # Inventory app endpoints
    # path('posflow/', include('inventory.urls')),

    # Loans app endpoints
    path('posflow/', include('loans.urls')),

    # Payments app endpoints
    # path('posflow/', include('payments.urls')), 'MISSING URL PARTTERNS'

    # Promotions app endpoints
    # path('posflow/', include('promotions.urls')),  'PROMOTIONS DOES NOT HAVE ANYTHING'

    # Reports app endpoints
    # path('posflow/', include('reports.urls')), 'REPORTS DOES NOT HAVE ANYTHING'

    # Sales app endpoints
    # path('posflow/', include('sales.urls')),

    # Suppliers app endpoints
    # path('posflow/', include('suppliers.urls')),

    # Taxes app endpoints
    # path('posflow/', include('taxes.urls')), 'TAXES DOES NOT HAVE ANYTHING'

    # Transactions app endpoints
    # path('posflow/', include('transactions.urls')),

    # Transfers app endpoints
    # path('posflow/', include('transfers.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)