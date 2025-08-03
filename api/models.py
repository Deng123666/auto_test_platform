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


class Environment(models.Model):
    """
    环境配置模型
    - project: 关联的项目 (外键)
    - name: 环境名称 (如 DEV/QA/PROD)
    - base_url: 接口基础URL
    - db_connection: SQLite数据库文件路径
    - headers: 全局HTTP头 (JSON格式)
    - variables: 环境变量 (JSON格式)
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='environments')
    name = models.CharField(max_length=50)
    base_url = models.URLField()
    db_connection = models.CharField(max_length=255, help_text="SQLite数据库文件绝对路径", null=True)
    headers = models.JSONField(default=dict, blank=True)
    variables = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('project', 'name')

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class API(models.Model):
    """
    接口定义模型
    - project: 关联的项目 (外键)
    - name: 接口名称
    - path: 接口路径 (不以/开头)
    - method: HTTP方法 (GET/POST/PUT/DELETE)
    - description: 接口描述 (可选)
    - created_at: 创建时间
    """
    METHOD_CHOICES = (
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='apis')
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('project', 'path', 'method')

    def __str__(self):
        return f"{self.method} {self.path}"


class TestCase(models.Model):
    """
    测试用例模型
    - project: 关联的项目 (外键)
    - name: 用例名称
    - description: 用例描述 (可选)
    - environment: 执行环境
    - setup_script: 前置脚本 (SQL)
    - teardown_script: 后置脚本 (SQL)
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='test_cases')
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    environment = models.ForeignKey(Environment, on_delete=models.SET_NULL, null=True, blank=True)
    setup_script = models.TextField(null=True, blank=True, help_text="SQL语句，执行前运行")
    teardown_script = models.TextField(null=True, blank=True, help_text="SQL语句，执行后运行")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('project', 'name')

    def __str__(self):
        return self.name


class TestStep(models.Model):
    """
    测试步骤模型
    - test_case: 关联的测试用例 (外键)
    - api: 关联的接口
    - order: 执行顺序 (序号)
    - request_data: 请求数据 (JSON格式)
    - sql_check: 数据库验证SQL
    - expected_result: 预期结果 (JSON格式)
    - timeout: 请求超时时间 (秒)
    - created_at: 创建时间
    """
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE, related_name='steps')
    api = models.ForeignKey(API, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    request_data = models.JSONField(default=dict, blank=True)
    sql_check = models.TextField(null=True, blank=True, help_text="验证数据库的SQL语句")
    expected_result = models.JSONField(default=dict, blank=True)
    timeout = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['test_case', 'order']

    def __str__(self):
        return f"Step {self.order} - {self.api}"


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
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    start_time = models.DateTimeField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    report = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.test_case} - {self.get_status_display()}"


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


# class ScheduledTest(models.Model):
#     FREQUENCY_CHOICES = [
#         ('DAILY', '每天'),
#         ('WEEKLY', '每周'),
#         ('MONTHLY', '每月'),
#         ('CUSTOM', '自定义')
#     ]
#
#     name = models.CharField(max_length=100)
#     test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE)
#     environment = models.ForeignKey(Environment, on_delete=models.CASCADE)
#     frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
#     cron_expression = models.CharField(max_length=50, blank=True, null=True)
#     next_run = models.DateTimeField()
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.nameclass ScheduledTest(models.Model):
#     FREQUENCY_CHOICES = [
#         ('DAILY', '每天'),
#         ('WEEKLY', '每周'),
#         ('MONTHLY', '每月'),
#         ('CUSTOM', '自定义')
#     ]
#
#     name = models.CharField(max_length=100)
#     test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE)
#     environment = models.ForeignKey(Environment, on_delete=models.CASCADE)
#     frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
#     cron_expression = models.CharField(max_length=50, blank=True, null=True)
#     next_run = models.DateTimeField()
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.name