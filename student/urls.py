from django.urls import path
from student.views import StudentLoginViews
from .views import GetStudents

student_endpoints = [
    path('login', StudentLoginViews.as_view()),
    path('students/', GetStudents.as_view(), name='get_students')
]



