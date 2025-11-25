# company/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include


from company.views.company_views import (
    CompanyViewSet, 
    CompanyLoginView,
    CompanyLogoutView,
    CompanyRegisterView, 
    CompanyUpdateView, 
    CompanyDeleteView,
    CompanyTokenRefreshView
)


router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')

urlpatterns = [
    path('company/login/', CompanyLoginView.as_view(), name='company-login'),
    path('company/logout/', CompanyLogoutView.as_view(), name='company-logout'),
    path('company/register/', CompanyRegisterView.as_view(), name='company-register'),
    path('company/token/refresh/', CompanyTokenRefreshView.as_view(), name='company-token-refresh'),
    path('company/<int:pk>/update/', CompanyUpdateView.as_view(), name='company-update'),
    path('company/<int:pk>/delete/', CompanyDeleteView.as_view(), name='company-delete'),
    path('', include(router.urls)),  # ReadOnly list/retrieve
]
