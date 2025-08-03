# from celery import shared_task
# from .test_runner import TestRunner
# from django.utils import timezone
# from datetime import timedelta, datetime
#
#
# @shared_task
# def run_test_execution(test_execution_id):
#     runner = TestRunner(test_execution_id)
#     runner.run()
#
#
# from celery import shared_task
# from django_celery_beat.models import PeriodicTask, CrontabSchedule
# from .models import ScheduledTest, TestExecution
#
#
# @shared_task
# def schedule_test_tasks():
#     """检查并执行计划的测试任务"""
#     now = timezone.now()
#     scheduled_tests = ScheduledTest.objects.filter(
#         next_run__lte=now,
#         is_active=True
#     )
#
#     for test in scheduled_tests:
#         # 创建执行记录
#         execution = TestExecution.objects.create(
#             test_case=test.test_case,
#             environment=test.environment,
#             status='PENDING'
#         )
#
#         # 执行测试
#         run_test_execution.delay(execution.id)
#
#         # 更新下次执行时间
#         test.next_run = calculate_next_run(test.frequency, test.cron_expression)
#         test.save()
#
#
# def calculate_next_run(frequency, cron_expr=None):
#     """计算下次执行时间"""
#     now = timezone.now()
#     if frequency == 'DAILY':
#         return now + timedelta(days=1)
#     elif frequency == 'WEEKLY':
#         return now + timedelta(weeks=1)
#     elif frequency == 'MONTHLY':
#         return now + timedelta(days=30)
#     elif frequency == 'CUSTOM' and cron_expr:
#         # 使用croniter解析cron表达式
#         from croniter import croniter
#         base = now
#         iter = croniter(cron_expr, base)
#         return iter.get_next(datetime)
#     return now + timedelta(days=1)  # 默认每天