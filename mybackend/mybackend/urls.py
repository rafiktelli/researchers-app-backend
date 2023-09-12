
from django.contrib import admin
from django.urls import path
from .views import add_teacher, get_teacher_list, get_teacher_by_email, get_publications_by_email

urlpatterns = [
    path('add_teacher/', add_teacher, name='add_teacher'),
    path('teachers_list/', get_teacher_list, name='teacher-list'),
    path('profile/<str:email>/', get_teacher_by_email, name='get_teacher_by_email'),
    path('publications/', get_publications_by_email, name='get_publications_by_email'),
]
