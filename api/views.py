from rest_framework import viewsets
# from rest_framework.response import Response
# from rest_framework.decorators import action
# from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import AllowAny  # 统一导入权限类

from .models import Project, TestCase, TestExecution, ApiConfig
from .serializers import ProjectSerializer, TestCaseSerializer, TestExecutionSerializer, ApiConfigSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-created_at')
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """可选：根据名称过滤项目"""
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class TestCaseViewSet(viewsets.ModelViewSet):
    serializer_class = TestCaseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """按项目过滤测试用例"""
        # 移除prefetch_related('steps')，因steps关联已删除
        queryset = TestCase.objects.all().order_by('project', 'name')
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset


class ApiConfigViewSet(viewsets.ModelViewSet):
    """
    API配置的CRUD操作视图集
    支持对测试用例接口配置的创建、查询、更新和删除
    """
    queryset = ApiConfig.objects.all()
    serializer_class = ApiConfigSerializer
    permission_classes = [AllowAny]  # 根据项目实际权限调整

    def get_queryset(self):
        """支持按测试用例ID筛选"""
        queryset = ApiConfig.objects.all()
        test_case_id = self.request.query_params.get('test_case_id')
        if test_case_id:
            queryset = queryset.filter(test_case_id=test_case_id)
        return queryset


class TestExecutionViewSet(viewsets.ModelViewSet):
    serializer_class = TestExecutionSerializer
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

        # # 使用Celery异步执行（保留注释，如需可恢复）
        # run_test_execution.delay(instance.id)

    # def run_test(self, test_execution_id):
    #     # 同步执行测试（保留注释，如需可恢复）
    #     runner = TestRunner(test_execution_id)
    #     runner.run()


# class TestReportView(TemplateView):
#     template_name = 'api/test_report.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         execution_id = self.kwargs['execution_id']
#         execution = get_object_or_404(TestExecution, id=execution_id)
#
#         # 准备报告数据
#         context['execution'] = execution
#         context['report'] = execution.report
#         context['steps'] = execution.report.get('steps', [])
#         context['summary'] = execution.report.get('summary', {})
#         context['errors'] = execution.report.get('errors', [])
#
#         return context