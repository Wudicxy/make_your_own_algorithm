from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """题目分类"""
    name = models.CharField(max_length=50, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'

    def __str__(self):
        return self.name


class Difficulty(models.Model):
    """难度等级"""
    LEVEL_CHOICES = [
        (1, '初级'),
        (2, '中级'),
        (3, '高级'),
        (4, '专家')
    ]

    level = models.IntegerField(choices=LEVEL_CHOICES, unique=True, verbose_name='难度等级')
    name = models.CharField(max_length=20, verbose_name='难度名称')

    class Meta:
        verbose_name = '难度'
        verbose_name_plural = '难度'

    def __str__(self):
        return self.name


class Question(models.Model):
    """八股文题目"""
    title = models.CharField(max_length=200, verbose_name='题目标题')
    content = models.TextField(verbose_name='题目内容')
    answer = models.TextField(verbose_name='参考答案')
    key_points = models.TextField(blank=True, verbose_name='关键要点')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='分类')
    difficulty = models.ForeignKey(Difficulty, on_delete=models.CASCADE, verbose_name='难度')
    tags = models.CharField(max_length=200, blank=True, verbose_name='标签')
    view_count = models.PositiveIntegerField(default=0, verbose_name='浏览次数')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '八股文题目'
        verbose_name_plural = '八股文题目'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_tags_list(self):
        """获取标签列表"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]


class UserFavorite(models.Model):
    """用户收藏"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='题目')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '用户收藏'
        verbose_name_plural = '用户收藏'
        unique_together = ['user', 'question']

    def __str__(self):
        return f'{self.user.username} - {self.question.title}'


class ImportRecord(models.Model):
    """导入记录"""
    IMPORT_TYPE_CHOICES = [
        ('excel', 'Excel文件'),
        ('json', 'JSON文件'),
        ('manual', '手动批量'),
        ('api', 'API导入'),
    ]

    import_type = models.CharField(max_length=20, choices=IMPORT_TYPE_CHOICES, verbose_name='导入类型')
    file_name = models.CharField(max_length=200, blank=True, verbose_name='文件名')
    total_count = models.PositiveIntegerField(default=0, verbose_name='总数量')
    success_count = models.PositiveIntegerField(default=0, verbose_name='成功数量')
    error_count = models.PositiveIntegerField(default=0, verbose_name='失败数量')
    error_log = models.TextField(blank=True, verbose_name='错误日志')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='导入人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='导入时间')

    class Meta:
        verbose_name = '导入记录'
        verbose_name_plural = '导入记录'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_import_type_display()} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'
