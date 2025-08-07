from django.contrib import admin
from django.urls import path, include
from question import views

urlpatterns = [
    path('', views.problem_list, name='problem_list'),
    path('update-status/<int:problem_id>/', views.update_problem_status, name='update_problem_status'),
    path('leetcode/update-mastery/<int:problem_id>/', views.update_mastery, name='update_mastery'),
    path('notes/<int:problem_id>/', views.problem_notes, name='problem_notes'),
    path('admin/', admin.site.urls),
    # 添加认证URL
    path('accounts/', include('django.contrib.auth.urls')),
    path('leetcode/update-status/<int:problem_id>/', views.update_problem_status, name='update_problem_status'),
    path('add/', views.add_problem, name='add_problem'),
    path('notes/', include('notes.urls', namespace='notes')),
    path('baguwen/', include('baguwen.urls')),  # 八股文app
    path('random/', views.random_problem, name='random'),

]
