# api/test_runner.py
import sqlite3
import requests
import time
from django.utils import timezone
from .models import TestExecution, TestCase, Environment, TestStep


class TestRunner:
    def __init__(self, test_execution_id):
        self.test_execution_id = test_execution_id
        self.test_execution = TestExecution.objects.get(id=test_execution_id)
        self.environment = self.test_execution.environment
        self.test_case = self.test_execution.test_case
        self.db_conn = None
        self.report = {
            'steps': [],
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'error': 0,
                'start_time': None,
                'duration': 0
            },
            'errors': []
        }

    def run(self):
        try:
            self._start_execution()
            self._run_setup_scripts()
            self._run_test_steps()
            self._run_teardown_scripts()
        except Exception as e:
            self._handle_execution_error(e)
        finally:
            self._cleanup_resources()
            self._finalize_execution()

    def _start_execution(self):
        self.test_execution.status = 'RUNNING'
        self.test_execution.start_time = timezone.now()
        self.test_execution.save()
        self.report['summary']['start_time'] = self.test_execution.start_time.isoformat()
        self.report['summary']['total'] = self.test_case.steps.count()

    def _run_setup_scripts(self):
        if self.test_case.setup_script:
            self.execute_sql(self.test_case.setup_script)

    def _run_test_steps(self):
        steps = self.test_case.steps.order_by('order')
        for step in steps:
            self._run_single_step(step)

    def _run_single_step(self, step):
        step_report = {
            'step_id': step.id,
            'name': step.api.name,
            'api': step.api.path,
            'method': step.api.method,
            'request': {},
            'response': None,
            'db_check': None,
            'status': 'PENDING',
            'duration': 0,
            'error': None
        }

        try:
            # 准备请求
            url = f"{self.environment.base_url}{step.api.path}"
            headers = {**self.environment.headers, **step.request_data.get('headers', {})}
            params = step.request_data.get('params', {})
            data = step.request_data.get('data', {})
            json_data = step.request_data.get('json', None)

            # 发送请求
            start_time = time.time()
            response = requests.request(
                method=step.api.method,
                url=url,
                headers=headers,
                params=params,
                data=data if not json_data else None,
                json=json_data,
                timeout=step.timeout
            )
            duration = time.time() - start_time

            # 记录响应
            step_report['request'] = {
                'url': url,
                'method': step.api.method,
                'headers': headers,
                'params': params,
                'data': data,
                'json': json_data
            }
            step_report['response'] = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'body': response.text
            }
            step_report['duration'] = duration

            # 验证响应状态码
            expected_status = step.expected_result.get('status_code', 200)
            if response.status_code == expected_status:
                step_report['status'] = 'PASSED'
                self.report['summary']['passed'] += 1
            else:
                step_report['status'] = 'FAILED'
                self.report['summary']['failed'] += 1
                raise Exception(f"期望状态码 {expected_status}，实际 {response.status_code}")

            # 数据库验证
            if step.sql_check:
                db_result = self.execute_sql(step.sql_check)
                step_report['db_check'] = {
                    'sql': step.sql_check,
                    'result': db_result
                }
                # 这里可以添加数据库断言逻辑

        except Exception as e:
            step_report['status'] = 'ERROR'
            step_report['error'] = str(e)
            self.report['summary']['error'] += 1
            self.report['errors'].append({
                'step_id': step.id,
                'error': str(e)
            })
        finally:
            self.report['steps'].append(step_report)

    def _run_teardown_scripts(self):
        if self.test_case.teardown_script:
            self.execute_sql(self.test_case.teardown_script)

    def _handle_execution_error(self, error):
        self.report['summary']['error'] += 1
        self.test_execution.status = 'ERROR'
        self.report['errors'].append({
            'global_error': str(error)
        })

    def _cleanup_resources(self):
        if self.db_conn:
            self.db_conn.close()

    def _finalize_execution(self):
        end_time = timezone.now()
        if self.test_execution.start_time:
            self.report['summary']['duration'] = (end_time - self.test_execution.start_time).total_seconds()

        if self.test_execution.status != 'ERROR':
            if self.report['summary']['failed'] > 0:
                self.test_execution.status = 'FAILED'
            elif self.report['summary']['error'] > 0:
                self.test_execution.status = 'ERROR'
            else:
                self.test_execution.status = 'PASSED'

        self.test_execution.duration = self.report['summary']['duration']
        self.test_execution.report = self.report
        self.test_execution.save()

    def execute_sql(self, sql):
        if not self.db_conn:
            self.db_conn = sqlite3.connect(self.environment.db_connection)
        cursor = self.db_conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()