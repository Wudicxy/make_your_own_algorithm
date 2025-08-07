# urls.py
from django.urls import path
from . import views

app_name = 'baguwen'

urlpatterns = [
    path('', views.question_list, name='question_list'),
    path('question/<int:pk>/', views.question_detail, name='question_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('favorites/', views.my_favorites, name='my_favorites'),
    path('random/', views.random_question, name='random_question'),
    path('toggle-favorite/<int:pk>/', views.toggle_favorite, name='toggle_favorite'),
    # 导入相关URL
    path('import/', views.import_questions, name='import_questions'),
    path('import/excel/', views.import_excel, name='import_excel'),
    path('import/json/', views.import_json, name='import_json'),
    path('import/manual/', views.import_manual, name='import_manual'),
    path('quick-add/', views.quick_add, name='quick_add'),
    path('download-template/', views.download_template, name='download_template'),
    path('import-record/<int:pk>/', views.import_record_detail, name='import_record_detail'),
]
