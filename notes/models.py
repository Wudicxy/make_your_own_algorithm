from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from question.models import Problem  # 假设 Problem 在 leetcode app 下

class Note(models.Model):
    """用户对某题的笔记"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField(verbose_name='笔记内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='最近更新时间')

    class Meta:
        unique_together = ('user', 'problem')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} 的笔记: {self.problem}"
