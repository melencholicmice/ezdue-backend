import os
import jwt
import datetime
from django.shortcuts import render
from utils.crypto import verify_password
from department.models import (
    DepartmentUser,
    DepartmentStudentsMapping
)
from student.models import Student
from utils.auth import DepartmentValidator
from utils.validator import ValidateSchema
from department.schema import (
    LoginSchema,
    AddStudentToDepartmentSchema
)
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

    def add_to_filter_obj(key,value,obj):
        obj[key] = value
        return value

    @DepartmentValidator()
    def get(self,request):
        # filter_obj = {}
        # cursor = request.query_params.get("cursor")
        # limit = request.query_params.get("limit")
        # if not limit:
        #     limit = self.DEFAULT_LIMIT

        # role = self.add_to_filter_obj("role",request.query_params.get("role"),filter_obj)
        ...









