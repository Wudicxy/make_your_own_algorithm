from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Company(models.Model):
    """公司模型"""
    name = models.CharField(max_length=100, verbose_name='公司名称')

    class Meta:
        verbose_name = '公司'
        verbose_name_plural = '公司'

    def __str__(self):
        return self.name


class Department(models.Model):
    """部门模型"""
    name = models.CharField(max_length=100, verbose_name='部门名称')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments')

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = '部门'

    def __str__(self):
        return self.name


class Position(models.Model):
    """岗位模型"""
    name = models.CharField(max_length=100, verbose_name='岗位名称')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='positions')

    class Meta:
        verbose_name = '岗位'
        verbose_name_plural = '岗位'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """题目标签"""
    name = models.CharField(max_length=50, verbose_name='标签名称')

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'

    def __str__(self):
        return self.name


class ProblemSet(models.Model):
    """题集"""
    name = models.CharField(max_length=100, verbose_name='题集名称')
    description = models.TextField(blank=True, verbose_name='描述')

    class Meta:
        verbose_name = '题集'
        verbose_name_plural = '题集'

    def __str__(self):
        return self.name


class Problem(models.Model):
    """题目模型"""
    DIFFICULTY_CHOICES = [
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难'),
    ]
    # ← 在这里添加：
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        verbose_name='标签',
        related_name='problems'
    )

    number = models.IntegerField(unique=True, verbose_name='题号')
    title = models.CharField(max_length=200, verbose_name='题目标题')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, verbose_name='难度')

    problem_sets = models.ManyToManyField(ProblemSet, blank=True, verbose_name='题集')
    companies = models.ManyToManyField(Company, through='CompanyProblem', blank=True, verbose_name='相关公司')
    leetcode_url = models.URLField(blank=True, verbose_name='LeetCode链接')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '题目'
        verbose_name_plural = '题目'
        ordering = ['number']

    def __str__(self):
        return f"{self.number}. {self.title}"


class CompanyProblem(models.Model):
    """公司题目关联（记录考察频度）"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    frequency = models.IntegerField(default=1, verbose_name='考察频度')
    last_asked = models.DateField(default=timezone.now, verbose_name='最近考察时间')
    positions = models.ManyToManyField(Position, blank=True, verbose_name='相关岗位')

    class Meta:
        verbose_name = '公司题目'
        verbose_name_plural = '公司题目'
        unique_together = ['company', 'problem']


class UserProblem(models.Model):
    """用户题目记录"""
    STATUS_CHOICES = [
        ('not_started', '未做'),
        ('completed', '完成'),
        ('attempted', '尝试过'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='problems')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='user_records')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started', verbose_name='状态')
    mastery = models.IntegerField(default=0, verbose_name='掌握程度', help_text='0-5星')
    notes = models.TextField(blank=True, verbose_name='笔记')
    last_practice = models.DateTimeField(null=True, blank=True, verbose_name='最近练习时间')
    practice_count = models.IntegerField(default=0, verbose_name='练习次数')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '用户题目记录'
        verbose_name_plural = '用户题目记录'
        unique_together = ['user', 'problem']