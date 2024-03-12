from rest_framework import serializers
from student.models import Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['roll_number', 'first_name', 'last_name', 'institute_email', 'joining_year', 'leaving_year', 'role', 'academic_program', 'is_active', 'deactivated_on']
