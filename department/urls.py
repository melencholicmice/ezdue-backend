from django.urls import path
from department.views import (
    DepartmentLogin,
    AddStudentToDepartment
)

department_endpoints = [
    path("login", DepartmentLogin.as_view(), name="Department Login"),
    path("add-student",AddStudentToDepartment.as_view(), name="Add student to department")
]