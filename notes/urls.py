from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('', views.list_notes, name='list_notes'),
    path('<int:problem_id>/edit/', views.edit_note, name='edit_note'),
    path('<int:problem_id>/delete/', views.delete_note, name='delete_note'),
]