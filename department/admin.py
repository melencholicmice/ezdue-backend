from django.contrib import admin
from department.models import (
    Department,
    DepartmentUser,
    DepartmentStudentsMapping
)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'email',
    )
    readonly_fields = ('id',)

class DepartmentUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'department',
        'is_active',
        'deactivated_on',
    )
    readonly_fields = ('id','deactivated_on',)


admin.site.register(Department,DepartmentAdmin)
admin.site.register(DepartmentUser,DepartmentUserAdmin)
admin.site.register(DepartmentStudentsMapping)


