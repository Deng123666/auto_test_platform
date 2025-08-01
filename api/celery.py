# auto_test_platform/celery.py
from celery import Celery
from celery.schedules import crontab

app = Celery('auto_test_platform')
app.config_from_object('django.conf:settings', namespace='CELERY')

# 定时任务
app.conf.beat_schedule = {
    'check-scheduled-tests': {
        'task': 'api.tasks.schedule_test_tasks',
        'schedule': crontab(minute='*/5'),  # 每5分钟检查一次
    },
}
app.autodiscover_tasks()