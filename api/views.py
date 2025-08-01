from rest_framework.permissions import AllowAny

from .models import Project, Environment, API, TestCase, TestStep
from .serializers import (
    ProjectSerializer,
    EnvironmentSerializer,
    APISerializer,
    TestCaseSerializer,
    TestExecutionSerializer, TestStepSerializer
)
from .test_runner import TestRunner
# from .tasks import run_test_execution
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from .models import TestExecution
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import authenticate, login, logout
from .models import User, RolePermission
from .serializers import UserSerializer, RolePermissionSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-created_at')
    serializer_class = ProjectSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [AllowAny]

    def get_queryset(self):
        """可选：根据名称过滤项目"""
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class EnvironmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnvironmentSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [AllowAny]

    def get_queryset(self):
        """按项目过滤环境"""
        queryset = Environment.objects.all().order_by('project', 'name')
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset


class APIViewSet(viewsets.ModelViewSet):
    serializer_class = APISerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [AllowAny]

    def get_queryset(self):
        """按项目过滤API"""
        queryset = API.objects.all().order_by('project', 'path')
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset


class TestCaseViewSet(viewsets.ModelViewSet):
    serializer_class = TestCaseSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [AllowAny]

    def get_queryset(self):
        """按项目过滤测试用例"""
        queryset = TestCase.objects.all().order_by('project', 'name').prefetch_related('steps')
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset


class TestStepViewSet(viewsets.ModelViewSet):
    serializer_class = TestStepSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [AllowAny]

    def get_queryset(self):
        """按测试用例过滤测试步骤"""
        queryset = TestStep.objects.all().order_by('test_case', 'order')
        test_case_id = self.request.query_params.get('test_case')
        if test_case_id:
            queryset = queryset.filter(test_case_id=test_case_id)
        return queryset


class TestExecutionViewSet(viewsets.ModelViewSet):
    serializer_class = TestExecutionSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [AllowAny]

    def get_queryset(self):
        """按测试用例过滤执行记录"""
        queryset = TestExecution.objects.all().order_by('-created_at')
        test_case_id = self.request.query_params.get('test_case')
        if test_case_id:
            queryset = queryset.filter(test_case_id=test_case_id)
        return queryset

    def perform_create(self, serializer):
        # 先保存实例，状态为PENDING
        instance = serializer.save(status='PENDING')

        # # 使用Celery异步执行
        # run_test_execution.delay(instance.id)

        self.run_test(instance.id)

    def run_test(self, test_execution_id):
        # 这里应该使用异步任务，暂时直接调用
        runner = TestRunner(test_execution_id)
        runner.run()


class TestReportView(TemplateView):
    template_name = 'api/test_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        execution_id = self.kwargs['execution_id']
        execution = get_object_or_404(TestExecution, id=execution_id)

        # 准备报告数据
        context['execution'] = execution
        context['report'] = execution.report
        context['steps'] = execution.report.get('steps', [])
        context['summary'] = execution.report.get('summary', {})
        context['errors'] = execution.report.get('errors', [])

        return context


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            # self.permission_classes = [permissions.IsAdminUser]
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({
                'user': UserSerializer(user).data,
                'message': '登录成功'
            })
        return Response({'error': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'message': '登出成功'})

    @action(detail=False, methods=['get'])
    def current_user(self, request):
        if request.user.is_authenticated:
            return Response(UserSerializer(request.user).data)
        return Response({'error': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        user = self.get_object()
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user.check_password(old_password):
            return Response({'error': '原密码错误'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': '密码修改成功'})


class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = [AllowAny]
