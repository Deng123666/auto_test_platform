from rest_framework import serializers
from .models import Project, TestCase, TestExecution, ApiConfig  # 移除Environment, API, TestStep引用


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        # 显式指定字段，替代__all__，避免模型变更时意外暴露字段
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        # 新增用例配置核心字段，移除steps关联字段
        # fields = [
        #     'id', 'project', 'name', 'description', 'url', 'method',
        #     'request_params', 'request_headers', 'request_body',
        #     'setup_script', 'teardown_script', 'expected_result',
        #     'timeout', 'created_at', 'updated_at'
        # ]
        fields = ['id', 'project', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ApiConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiConfig
        fields = [
            'id', 'test_case', 'url', 'method', 'query_params',
            'header_params', 'body_type', 'raw_type', 'raw_body',
            'body_params', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_test_case(self, value):
        """仅在创建新配置时检查唯一性，更新时跳过"""
        # self.instance存在表示是更新操作，不需要检查
        if self.instance is None and ApiConfig.objects.filter(test_case=value).exists():
            raise serializers.ValidationError("该测试用例已存在接口配置")
        return value



class TestExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestExecution
        # 显式指定字段，移除environment（若Environment模型已简化）
        fields = ['id', 'test_case', 'status', 'start_time', 'duration', 'report', 'created_at']
        read_only_fields = ['start_time', 'duration', 'report', 'created_at']
