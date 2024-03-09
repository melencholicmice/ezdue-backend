from django.urls import path
from department.views import DepartmentLogin

department_endpoints = [
    path("login", DepartmentLogin.as_view(), name="Department Login")
]