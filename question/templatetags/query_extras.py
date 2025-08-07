# templatetags/query_extras.py
from django import template
from django.http import QueryDict
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag
def query_transform(request, **kwargs):
    """
    保持现有URL参数，只更新指定的参数
    用法: {% query_transform request page=2 sort='title' %}
    """
    query_dict = request.GET.copy()
    for key, value in kwargs.items():
        if value is None:
            query_dict.pop(key, None)
        else:
            query_dict[key] = value
    return query_dict.urlencode()

@register.simple_tag
def url_replace(request, field, value):
    """替换URL中的查询参数，保持其他参数不变"""
    query_dict = request.GET.copy()
    query_dict[field] = value
    return '?' + query_dict.urlencode()

@register.simple_tag
def get_sort_direction(request, field):
    """获取排序方向图标"""
    current_sort = request.GET.get('sort', '')
    if current_sort == field:
        return '↑'
    elif current_sort == f'-{field}':
        return '↓'
    else:
        return '↕'
