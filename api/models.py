from django.db import models
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _


class Project(models.Model):
    """
    项目管理模型
    - name: 项目名称 (唯一标识)
    - description: 项目描述 (可选)
    - created_at: 创建时间 (自动记录)
    - updated_at: 更新时间 (自动更新)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TestCase(models.Model):
    """
    测试用例模型
    - project: 关联的项目 (外键)
    - name: 用例名称
    - description: 用例描述 (可选)
    - setup_script: 前置脚本 (SQL)
    - teardown_script: 后置脚本 (SQL)
    - expected_result: 预期结果 (JSON格式)
    - timeout: 请求超时时间 (秒)
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    # 移除 METHOD_CHOICES（已在 ApiConfig 中定义）

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='test_cases')
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    setup_script = models.TextField(null=True, blank=True, help_text="SQL语句，执行前运行")
    teardown_script = models.TextField(null=True, blank=True, help_text="SQL语句，执行后运行")
    expected_result = models.JSONField(null=True, default=dict, blank=True)
    timeout = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('project', 'name')

    def __str__(self):
        return self.name


class ApiConfig(models.Model):
    """
    API配置模型，存储测试用例的接口配置详情
    """
    BODY_TYPE_CHOICES = (
        ('form-data', 'form-data'),
        ('x-www-form-urlencoded', 'x-www-form-urlencoded'),
        ('raw', 'raw'),
        ('binary', 'binary'),
    )
    RAW_TYPE_CHOICES = (
        ('text', 'Text'),
        ('javascript', 'JavaScript'),
        ('json', 'JSON'),
        ('html', 'HTML'),
        ('xml', 'XML'),
    )
    METHOD_CHOICES = (
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH'),
    )

    test_case = models.OneToOneField(
        TestCase,
        on_delete=models.CASCADE,
        related_name='api_config',
        help_text="关联的测试用例"
    )
    url = models.URLField(help_text="请求完整URL")
    method = models.CharField(
        max_length=10,
        choices=METHOD_CHOICES,
        default='GET',
        help_text="HTTP请求方法"
    )
    query_params = models.JSONField(
        default=list,
        help_text="Query参数列表，格式: [{'key': 'xxx', 'value': 'xxx'}, ...]"
    )
    header_params = models.JSONField(
        default=list,
        help_text="请求头参数列表，格式: [{'key': 'xxx', 'value': 'xxx'}, ...]"
    )
    body_type = models.CharField(
        max_length=30,
        choices=BODY_TYPE_CHOICES,
        default='form-data',
        help_text="请求体类型"
    )
    raw_type = models.CharField(
        max_length=20,
        choices=RAW_TYPE_CHOICES,
        default='json',
        null=True,
        blank=True,
        help_text="raw类型请求体的格式"
    )
    raw_body = models.TextField(
        blank=True,
        null=True,
        help_text="raw类型请求体内容"
    )
    body_params = models.JSONField(
        default=list,
        help_text="form-data/x-www-form-urlencoded参数列表，格式: [{'key': 'xxx', 'value': 'xxx'}, ...]"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.test_case.name} - 接口配置"


class TestExecution(models.Model):
    """
    测试执行记录模型
    - test_case: 关联的测试用例
    - environment: 执行环境
    - status: 执行状态
    - start_time: 开始时间
    - duration: 执行时长 (秒)
    - report: 测试报告 (JSON格式)
    - created_at: 创建时间
    """
    STATUS_CHOICES = (
        ('PENDING', '待执行'),
        ('RUNNING', '执行中'),
        ('PASSED', '通过'),
        ('FAILED', '失败'),
        ('ERROR', '错误'),
    )

    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    start_time = models.DateTimeField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    report = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.test_case} - {self.get_status_display()}"