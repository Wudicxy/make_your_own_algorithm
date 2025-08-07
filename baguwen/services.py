# services.py
import pandas as pd
import json
from django.db import transaction
from .models import Question, Category, Difficulty, ImportRecord


class QuestionImportService:
    """题目导入服务"""

    def __init__(self, user=None):
        self.user = user
        self.errors = []

    def import_from_excel(self, excel_file):
        """从Excel导入题目"""
        try:
            # 读取Excel文件
            df = pd.read_excel(excel_file)

            # 验证必要列
            required_columns = ['title', 'content', 'answer', 'category', 'difficulty']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f'Excel文件缺少必要列：{", ".join(missing_columns)}')

            # 创建导入记录
            import_record = ImportRecord.objects.create(
                import_type='excel',
                file_name=excel_file.name,
                total_count=len(df),
                created_by=self.user
            )

            success_count = 0
            error_log = []

            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # 获取或创建分类
                        category, _ = Category.objects.get_or_create(
                            name=row['category'],
                            defaults={'description': f'从Excel导入的分类：{row["category"]}'}
                        )

                        # 获取难度
                        difficulty_map = {'初级': 1, '中级': 2, '高级': 3, '专家': 4}
                        difficulty_level = difficulty_map.get(row['difficulty'], 2)
                        difficulty = Difficulty.objects.get(level=difficulty_level)

                        # 创建题目
                        Question.objects.create(
                            title=row['title'],
                            content=row['content'],
                            answer=row['answer'],
                            key_points=row.get('key_points', ''),
                            category=category,
                            difficulty=difficulty,
                            tags=row.get('tags', ''),
                        )

                        success_count += 1

                    except Exception as e:
                        error_msg = f'第{index + 2}行导入失败：{str(e)}'
                        error_log.append(error_msg)
                        continue

            # 更新导入记录
            import_record.success_count = success_count
            import_record.error_count = len(error_log)
            import_record.error_log = '\n'.join(error_log)
            import_record.save()

            return import_record

        except Exception as e:
            raise ValueError(f'Excel导入失败：{str(e)}')

    def import_from_json(self, json_file):
        """从JSON导入题目"""
        try:
            data = json.load(json_file)
            if not isinstance(data, list):
                raise ValueError('JSON文件格式错误：根元素必须是数组')

            return self._import_from_data(data, 'json', json_file.name)

        except json.JSONDecodeError:
            raise ValueError('JSON文件格式错误')

    def import_from_manual_data(self, questions_data):
        """从手动输入的数据导入"""
        return self._import_from_data(questions_data, 'manual', '手动批量添加')

    def _import_from_data(self, questions_data, import_type, file_name):
        """从数据导入题目的通用方法"""
        import_record = ImportRecord.objects.create(
            import_type=import_type,
            file_name=file_name,
            total_count=len(questions_data),
            created_by=self.user
        )

        success_count = 0
        error_log = []

        with transaction.atomic():
            for i, question_data in enumerate(questions_data):
                try:
                    # 获取或创建分类
                    category, _ = Category.objects.get_or_create(
                        name=question_data['category'],
                        defaults={'description': f'从{import_type}导入的分类'}
                    )

                    # 获取难度
                    difficulty_map = {'初级': 1, '中级': 2, '高级': 3, '专家': 4}
                    difficulty_level = difficulty_map.get(question_data['difficulty'], 2)
                    difficulty = Difficulty.objects.get(level=difficulty_level)

                    # 创建题目
                    Question.objects.create(
                        title=question_data['title'],
                        content=question_data['content'],
                        answer=question_data['answer'],
                        key_points=question_data.get('key_points', ''),
                        category=category,
                        difficulty=difficulty,
                        tags=question_data.get('tags', ''),
                    )

                    success_count += 1

                except Exception as e:
                    error_msg = f'第{i + 1}个题目导入失败：{str(e)}'
                    error_log.append(error_msg)
                    continue

        # 更新导入记录
        import_record.success_count = success_count
        import_record.error_count = len(error_log)
        import_record.error_log = '\n'.join(error_log)
        import_record.save()

        return import_record
