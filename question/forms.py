# leetcode/forms.py
from django import forms
from .models import Problem

class ProblemForm(forms.ModelForm):
    company_name = forms.CharField(label="公司", required=False)
    department_name = forms.CharField(label="部门", required=False)

    class Meta:
        model = Problem
        fields = ['number', 'title', 'difficulty', 'tags', 'problem_sets', 'leetcode_url']
        widgets = {
            'tags': forms.CheckboxSelectMultiple,
            'problem_sets': forms.CheckboxSelectMultiple,
        }
