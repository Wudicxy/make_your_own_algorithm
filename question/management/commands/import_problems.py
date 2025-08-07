import json
from django.core.management.base import BaseCommand
from question.models import Problem, Tag

class Command(BaseCommand):
    help = "从 JSON 文件导入 LeetCode 题目（自动创建标签并关联）"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="data/leetcode_problems.json",
            help="JSON 文件路径（默认 data/leetcode_problems.json）"
        )

    def handle(self, *args, **options):
        file_path = options["file"]
        self.stdout.write(f"读取 {file_path} ...")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"文件 {file_path} 不存在"))
            return

        count = 0
        for item in data:
            # 1. 创建或更新题目
            problem, created = Problem.objects.update_or_create(
                number=item["number"],
                defaults={
                    "title": item["title"],
                    "difficulty": item["difficulty"],
                    "url": item["url"],
                }
            )
            # 2. 处理标签
            tag_objs = [Tag.objects.get_or_create(name=t)[0] for t in item.get("tags", [])]
            problem.tags.set(tag_objs)  # 多对多赋值
            count += 1

        self.stdout.write(self.style.SUCCESS(f"成功导入/更新 {count} 道题目"))
