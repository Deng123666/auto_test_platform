from django.template.loader import render_to_string
from weasyprint import HTML
import os
from django.conf import settings


def generate_test_report(test_execution):
    """生成HTML和PDF格式的测试报告"""
    # 准备报告数据
    context = {
        'execution': test_execution,
        'steps': test_execution.report.get('steps', []),
        'summary': test_execution.report.get('summary', {})
    }

    # 生成HTML报告
    html_content = render_to_string('api/test_report.html', context)

    # 生成PDF报告
    pdf_path = os.path.join(settings.MEDIA_ROOT, f'reports/{test_execution.id}.pdf')
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    HTML(string=html_content).write_pdf(pdf_path)

    return {
        'html': html_content,
        'pdf_path': pdf_path
    }