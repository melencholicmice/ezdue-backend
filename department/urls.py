from django.urls import path
from department.views import (
    DepartmentLogin,
    AddStudentToDepartment,
    GetDepartmentStudents,
    GetDues
)

department_endpoints = [
    path("login", DepartmentLogin.as_view(), name="Department Login"),
    path("add-student",AddStudentToDepartment.as_view(), name="Add student to department"),
    path("dues", GetDues.as_view(), name="Get Dues"),
    path("students", GetDepartmentStudents.as_view(), name="Get students in a Department")
]