from django.urls import path
from student.views import StudentLoginViews

student_endpoints = [
    path('login', StudentLoginViews.as_view())
]
