from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet,
    EnvironmentViewSet,
    APIViewSet,
    TestCaseViewSet,
    TestExecutionViewSet,
    TestStepViewSet, UserViewSet, RolePermissionViewSet
)

router = DefaultRouter()

router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'environments', EnvironmentViewSet, basename='environment')
router.register(r'apis', APIViewSet, basename='api')
router.register(r'test-cases', TestCaseViewSet, basename='testcase')
router.register(r'test-executions', TestExecutionViewSet, basename='testexecution')
router.register(r'test-steps', TestStepViewSet, basename='teststep')
router.register(r'users', UserViewSet, basename='user')
router.register(r'role-permissions', RolePermissionViewSet, basename='role-permission')

urlpatterns = [
    path('', include(router.urls)),
]