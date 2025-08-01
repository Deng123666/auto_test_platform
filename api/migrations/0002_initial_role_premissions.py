# api/migrations/0002_initial_role_permissions.py
from django.db import migrations


def create_initial_role_permissions(apps, schema_editor):
    RolePermission = apps.get_model('api', 'RolePermission')

    # 管理员权限
    RolePermission.objects.create(role='admin', permission='manage_users')
    RolePermission.objects.create(role='admin', permission='manage_projects')
    RolePermission.objects.create(role='admin', permission='execute_tests')
    RolePermission.objects.create(role='admin', permission='view_reports')

    # 项目管理权限
    RolePermission.objects.create(role='manager', permission='manage_projects')
    RolePermission.objects.create(role='manager', permission='execute_tests')
    RolePermission.objects.create(role='manager', permission='view_reports')

    # 测试人员权限
    RolePermission.objects.create(role='tester', permission='execute_tests')
    RolePermission.objects.create(role='tester', permission='view_reports')

    # 只读用户权限
    RolePermission.objects.create(role='viewer', permission='view_reports')


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_role_permissions),
    ]