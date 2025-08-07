from django.contrib import admin

# Register your models here.
# admin.py
from django.contrib import admin
from .models import Category, Difficulty, Question, UserFavorite


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(Difficulty)
class DifficultyAdmin(admin.ModelAdmin):
    list_display = ['level', 'name']
    ordering = ['level']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'view_count', 'is_active', 'created_at']
    list_filter = ['category', 'difficulty', 'is_active', 'created_at']
    search_fields = ['title', 'content', 'tags']
    list_editable = ['is_active']
    readonly_fields = ['view_count', 'created_at', 'updated_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'category', 'difficulty', 'tags', 'is_active')
        }),
        ('内容', {
            'fields': ('content', 'answer', 'key_points')
        }),
        ('统计信息', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'created_at']
    list_filter = ['created_at']
