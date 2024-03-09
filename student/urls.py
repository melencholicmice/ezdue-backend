from django.urls import path
from student.views import StudentLogin

student_endpoints = [
    path('login', StudentLogin.as_view())
]
