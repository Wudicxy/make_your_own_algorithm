from django.core.management.base import BaseCommand
from question.models import Problem, Tag
import json


class Command(BaseCommand):
    help = '导入LeetCode题目数据'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='JSON数据文件路径')

    def handle(self, *args, **options):
        file_path = options['file_path']

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            problem, created = Problem.objects.update_or_create(
                number=item['number'],
                defaults={
                    'title': item['title'],
                    'difficulty': item['difficulty'],
                    'leetcode_url': item.get('url', ''),
                }
            )

            # 添加标签
            for tag_name in item.get('tags', []):
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                problem.tags.add(tag)

            if created:
                self.stdout.write(f"创建题目: {problem}")
            else:
                self.stdout.write(f"更新题目: {problem}")