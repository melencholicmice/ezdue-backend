from django.urls import path
from student.views import (
    StudentLogin,
    StudentDepartmentData,
    StudentLoginBypass,
    GenerateNoDueCertificate
)

student_endpoints = [
    path('login', StudentLogin.as_view()),
    path('all-department-data-min',StudentDepartmentData.as_view()),
    path('login-bypass', StudentLoginBypass.as_view(), name="Login Bypass"),
    path('generate-no-due-certificate', GenerateNoDueCertificate.as_view(), name="Generate No Due Certificate")
]



