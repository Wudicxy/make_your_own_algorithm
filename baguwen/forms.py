# forms.py
from django import forms
from .models import Question, Category, Difficulty
import json


class ExcelImportForm(forms.Form):
    """Excel导入表单"""
    excel_file = forms.FileField(
        label='Excel文件',
        help_text='支持.xlsx和.xls格式，请按照模板格式填写',
        widget=forms.FileInput(attrs={'accept': '.xlsx,.xls'})
    )


class JSONImportForm(forms.Form):
    """JSON导入表单"""
    json_file = forms.FileField(
        label='JSON文件',
        help_text='请上传符合格式要求的JSON文件',
        widget=forms.FileInput(attrs={'accept': '.json'})
    )


class ManualBatchForm(forms.Form):
    """手动批量添加表单"""
    questions_data = forms.CharField(
        label='批量题目数据',
        widget=forms.Textarea(attrs={
            'rows': 15,
            'placeholder': '''请按以下JSON格式输入题目数据：
[
  {
    "title": "什么是TCP三次握手？",
    "content": "请详细解释TCP三次握手的过程",
    "answer": "TCP三次握手是建立连接的过程...",
    "key_points": "SYN, ACK, 连接建立",
    "category": "网络协议",
    "difficulty": "中级",
    "tags": "TCP,网络,协议"
  }
]'''
        })
    )

    def clean_questions_data(self):
        data = self.cleaned_data['questions_data']
        try:
            questions = json.loads(data)
            if not isinstance(questions, list):
                raise forms.ValidationError('数据格式错误：请提供题目数组')

            for i, question in enumerate(questions):
                required_fields = ['title', 'content', 'answer', 'category', 'difficulty']
                for field in required_fields:
                    if field not in question:
                        raise forms.ValidationError(f'第{i + 1}个题目缺少必填字段：{field}')

            return questions
        except json.JSONDecodeError:
            raise forms.ValidationError('JSON格式错误，请检查语法')


class QuickAddForm(forms.ModelForm):
    """快速添加单个题目"""

    class Meta:
        model = Question
        fields = ['title', 'content', 'answer', 'key_points', 'category', 'difficulty', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'key_points': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '用逗号分隔多个标签'}),
        }
