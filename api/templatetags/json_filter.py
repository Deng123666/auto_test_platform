import json
from django import template

register = template.Library()

@register.filter
def json(value):
    """将 Python 对象格式化为 JSON 字符串"""
    return json.dumps(value, indent=4, ensure_ascii=False)