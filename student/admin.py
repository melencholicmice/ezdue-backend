from django.contrib import admin
from student.models import Student
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'roll_number',
        'first_name' ,
        'last_name',
        'role' ,
        'academic_program' ,
        'is_active',
    )
    readonly_fields = ('deactivated_on',)

admin.site.register(Student,StudentAdmin)

