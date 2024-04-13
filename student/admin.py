import csv
from django.contrib import admin
from student.models import Student
from django.shortcuts import render
from student.forms import CSVUploadForm

def import_csv(modeladmin, request, queryset):
    form = CSVUploadForm()
    return render(request, 'admin/student/csv_upload_form.html', {'form': form})

import_csv.short_description = "Import CSV"

class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'roll_number',
        'first_name',
        'last_name',
        'role',
        'academic_program',
        'is_active',
    )
    readonly_fields = ('deactivated_on',)
    actions = [import_csv]



admin.site.register(Student, StudentAdmin)
