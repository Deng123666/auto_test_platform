from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet,
    TestCaseViewSet, ApiConfigViewSet, TestExecutionViewSet,
    #     TestExecutionViewSet,
)

router = DefaultRouter()

router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'test-cases', TestCaseViewSet, basename='testcase')
router.register(r'api-config', ApiConfigViewSet)
router.register(r'test-executions', TestExecutionViewSet, basename='testexecution')
# router.register(r'users', UserViewSet, basename='user')
# router.register(r'role-permissions', RolePermissionViewSet, basename='role-permission')

urlpatterns = [
    path('', include(router.urls)),
]