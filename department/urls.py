from django.urls import path
from department.views import (
    GetDues,
    GetDueById,
    DepartmentLogin,
    GetDepartmentStudents,
    AddStudentToDepartment,
    EditCertificateHTMLTemplate,
    ToggleCertificateGenerationPermission,
    get_template_variables
)

department_endpoints = [
    path("login", DepartmentLogin.as_view(), name="Department Login"),
    path("add-student",AddStudentToDepartment.as_view(), name="Add student to department"),
    path("due/<uuid:due_id>", GetDueById.as_view() ,name="Get Due by Id"),
    path("dues", GetDues.as_view(), name="Get Dues"),
    path("students", GetDepartmentStudents.as_view(), name="Get students in a Department"),
    path("switch-certificate-generation-permission", ToggleCertificateGenerationPermission.as_view(), name="Toggle certificate generation permission"),
    path("edit-certificate-tempate", EditCertificateHTMLTemplate.as_view(), name="Edit Certificate Template"),
    path("get-template-variables", get_template_variables, name="Get Available Template Variables")
]