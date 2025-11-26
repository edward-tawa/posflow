from rest_framework.routers import DefaultRouter
from branch.views.branch_views import BranchViewSet
from django.urls import path, include

router = DefaultRouter()

router.register(r'branches', BranchViewSet, basename='branch')

urlpatterns = [
    path('', include(router.urls))
]