import os
import jwt
import json
import datetime
from django.shortcuts import render
from utils.crypto import (
    verify_password,
    decode_cursor,
    encode_cursor
)
from department.models import (
    DepartmentUser,
    DepartmentStudentsMapping
)
from due.models import Due
from student.models import Student
from utils.auth import DepartmentValidator
from utils.validator import ValidateSchema
from department.schema import (
    LoginSchema,
    AddStudentToDepartmentSchema
)
from django.db.models import Count
from django.core.serializers import serialize
from rest_framework.views import APIView
from rest_framework.response import Response


class DepartmentLogin(APIView):
    @DepartmentValidator()
    def get(self, request):
        response = Response()
        response.data = {
            "username":request.department_user.username,
            "department_name":request.department_user.department.name,
            "message":"login successful"
        }
        response.status_code = 200
        return response

    @ValidateSchema(LoginSchema)
    def post(self, request):
        response = Response()

        username = request.data['username']
        password = request.data['password']

        try:
            department_user = DepartmentUser.objects.get(username=username)
        except Exception as e:
            response.data = {"message":"Invalid credentials, please try again"}
            response.status_code = 401
            return response

        if not verify_password(
            password=password,
            hashed_password=department_user.password
        ):
            response.data = {"message":"Invalid credentials, please try again"}
            response.status_code = 401
            return response

        payload = {
            "id": str(department_user.id),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60*24*2),
            "iat": datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, os.getenv("COOKIE_ENCRYPTION_SECRET") or "fallback_secret", algorithm='HS256')

        response.set_cookie(key='Authorization', value=token, httponly=True, samesite=None)
        response.data = {"message":"Login Succesful"}
        return response

class AddStudentToDepartment(APIView):
    @DepartmentValidator()
    @ValidateSchema(AddStudentToDepartmentSchema)
    def post(self,request):
        student_roll_number = request.data['roll_number']
        student_roll_number = student_roll_number.lower()
        response = Response()

        try:
            student = Student.objects.get(roll_number=student_roll_number)
        except Student.DoesNotExist as e:
            response.data = {"message":"Student with given data does not exist"}
            response.status_code = 404
            return response
        except Exception as e:
            print(str(e))
            response.data = {"message":"Internal server error"}
            response.status_code = 500
            return response

        try:
            existing_mapping = DepartmentStudentsMapping.objects.get(
                student = student,
                department = request.department_user.department
            )
            response.data = {"message":"This student already exists in this department"}
            response.status_code = 401
            return response
        except DepartmentStudentsMapping.DoesNotExist as e:
            pass
        except Exception as e:
            print(str(e))
            print(existing_mapping.__dict__)
            response.data = {"message":"Internal server error"}
            response.status_code = 500
            return response

        try:
            mapping = DepartmentStudentsMapping.objects.create(
                student = student,
                department = request.department_user.department
            )
            response.data = {"message":"Student added to department"}
            response.status_code = 201
        except Exception as e:
            print(str(e))
            response.data = {
                "message":"Failed to add student, please try again later if issue persists please contact admin"
                }
            response.status_code = 500

        return response

class GetDepartmentStudents(APIView):
    DEFAULT_LIMIT = 10

    @DepartmentValidator()
    def get(self,request):
        limit = int(request.query_params.get('limit', self.DEFAULT_LIMIT))
        cursor_value = request.query_params.get('cursor', None)

        if cursor_value is not None:
            cursor = decode_cursor(cursor_value)
        else:
            cursor = 0

        response = Response()
        filters = {}

        # Getting and building filters
        role = request.query_params.get('role', None)
        academic_program = request.query_params.get('academic_program',None)
        joining_year = request.query_params.get('joining_year',None)

        filters['department__id'] = request.department_user.department.id
        filters['student__is_active'] = True

        if role:
            filters['student__role'] = role
        if academic_program:
            filters['student__academic_program'] = academic_program
        if joining_year:
            filters['student__joining_year'] = joining_year

        try:
            count_query = DepartmentStudentsMapping.objects.filter(**filters).aggregate(total_size=Count('id'))
            total_size = count_query['total_size']

            query = DepartmentStudentsMapping.objects.filter(**filters)[cursor:cursor+limit]
            print(query.query)
            data = []
        except Exception as e:
            print(str(e))
            response.data = {"message":"Internal server error"}
            response.status_code = 500
            return response

        for obj in query:
            data.append({
                'last_name':obj.student.last_name,
                'first_name':obj.student.first_name,
                'academic_program':obj.student.academic_program,
                'role':obj.student.role,
                'institute_email':obj.student.institute_email,
                'joining_year':obj.student.joining_year
            })

        next_cursor = cursor + limit
        previous_cursor = max(cursor - limit, 0)

        next_url = f"?limit={limit}&cursor={encode_cursor(next_cursor)}" if next_cursor < total_size else None
        previous_url = f"?limit={limit}&cursor={encode_cursor(previous_cursor)}" if cursor > 0 else None
        if total_size == 0:
            next_url = previous_url = None
        response.data = {
            "total": total_size,
            "data": data,
            "next": next_url,
            "previous": previous_url
        }
        response.status_code = 200
        return response


class GetDues(APIView):
    DEFAULT_LIMIT = 10
    @DepartmentValidator()
    def get(self,request):
        limit = int(request.query_params.get('limit', self.DEFAULT_LIMIT))
        cursor_value = request.query_params.get('cursor', None)

        if cursor_value is not None:
            cursor = decode_cursor(cursor_value)
        else:
            cursor = 0

        response = Response()
        filters = {}

        # Getting and building filters
        role = request.query_params.get('role', None)
        academic_program = request.query_params.get('academic_program',None)
        joining_year = request.query_params.get('joining_year',None)
        due_date = request.query_params.get('due_date', None)
        due_date_lt = request.query_params.get('due_date_lt', None)
        due_date_gt = request.query_params.get('due_date_gt', None)

        filters['department__id'] = request.department_user.department.id
        filters['student__is_active'] = True

        if role:
            filters['student__role'] = role
        if academic_program:
            filters['student__academic_program'] = academic_program
        if joining_year:
            filters['student__joining_year'] = joining_year
        if due_date:
            filters['due_date'] = due_date
        if not due_date and due_date_gt:
            filters['due_date__gt'] = due_date_gt
        if not due_date and due_date_lt:
            filters['due_date__lt'] = due_date_lt

        try:
            count_query = Due.objects.filter(**filters).aggregate(total_size=Count('id'))
            total_size = count_query['total_size']

            query = Due.objects.filter(**filters)[cursor:cursor+limit]
            print(query.query)
            data = []
        except Exception as e:
            print(str(e))
            response.data = {"message":"Internal server error"}
            response.status_code = 500
            return response

        for obj in query:
            data.append({
                'amount':obj.amount,
                'due_date':obj.due_date,
                'roll_number':obj.student.roll_number,
                'status':obj.status,
                'reason':obj.reason,
                'created_at':obj.created_at,
            })

        next_cursor = cursor + limit
        previous_cursor = max(cursor - limit, 0)

        next_url = f"?limit={limit}&cursor={encode_cursor(next_cursor)}" if next_cursor < total_size else None
        previous_url = f"?limit={limit}&cursor={encode_cursor(previous_cursor)}" if cursor > 0 else None
        if total_size == 0:
            next_url = previous_url = None
        response.data = {
            "total": total_size,
            "data": data,
            "next": next_url,
            "previous": previous_url
        }
        response.status_code = 200
        return response
