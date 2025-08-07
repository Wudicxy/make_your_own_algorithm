from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Company, Department, Position, Tag, ProblemSet, Problem, CompanyProblem, UserProblem

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['number', 'title', 'difficulty']
    list_filter = ['difficulty', 'tags']
    search_fields = ['title', 'number']
    filter_horizontal = ['tags', 'problem_sets']

@admin.register(CompanyProblem)
class CompanyProblemAdmin(admin.ModelAdmin):
    list_display = ['company', 'problem', 'frequency', 'last_asked']
    list_filter = ['company', 'last_asked']
    date_hierarchy = 'last_asked'

# 注册其他模型
admin.site.register(Department)
admin.site.register(Position)
admin.site.register(Tag)
admin.site.register(ProblemSet)
admin.site.register(UserProblem)