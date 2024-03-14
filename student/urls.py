from django.urls import path
from student.views import StudentLogin, StudentDepartmentData

student_endpoints = [
    path('login', StudentLogin.as_view()),
    path('all-department-data-min',StudentDepartmentData.as_view())
]



