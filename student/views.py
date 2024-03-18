import jwt
from os import getenv
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from student.msal_plugin import MsLoginPlugin
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from student.models import Student
from department.models import DepartmentStudentsMapping, Department
from utils.validator import ValidateSchema
from utils.auth import StudentValidator
from student.schema import (
    StudentLoginSchema,
    StudentLoginBypassSchema,
    GenerateNoDueCertificateSchema
)


class StudentLogin(APIView):
    def __init__(self):
        self.ms_plugin = MsLoginPlugin(
            client_id=getenv("MSAL_CLIENT_ID"),
            client_secret=getenv("MSAL_CLIENT_SECRET")
        )

    def get(self,request):
        response = Response()
        token = request.COOKIES.get('Authorization')
        correct_token = False

        if token:
            try:
                payload = jwt.decode(token, getenv("COOKIE_ENCRYPTION_SECRET") or "fallback_secret", algorithms='HS256')
                student = Student.objects.get(roll_number=payload["roll_number"])
                if student:
                    correct_token = True
            except:
                pass

        if correct_token:
            response.data  = {"message":"Login successful."}
            response.status_code = 200
            return response

        try:
            url = self.ms_plugin.get_auth_url()
            response.data = {"login_url":url}
            response.status_code = 200
        except Exception as e:
            print(str(e))
            response.data = {"message":"Some error occured, try again"}
            response.status_code = 500

        return response

    @ValidateSchema(StudentLoginSchema)
    def post(self,request):
        access_code = request.data['access_code']
        response = Response()
        try:
            access_token = self.ms_plugin.get_access_token(
                authorization_code=access_code
            )
        except Exception as e:
            print(str(e))
            response.data = {"message":"Invalid credentials, please try again"}
            response.status_code = 401
            return response

        profile_data = self.ms_plugin.get_profile_data(
            access_token=access_token
        )

        if not profile_data:
            response.data = {"message":"Invalid credentials, please try again"}
            response.status_code = 401
            return response

        student_instance = self.ms_plugin.validate_profile_data(user_data=profile_data)
        if not student_instance:
            response.data = {"message":"User not found in database, please contact admin"}
            response.status_code = 404
            return response

        payload = {
            "institute_email":student_instance.institute_email,
            "roll_number":student_instance.roll_number,
            "exp": datetime.utcnow() + timedelta(days=2),
            "iat": datetime.utcnow()
        }

        try:
            token = jwt.encode(payload, getenv("COOKIE_ENCRYPTION_SECRET") or "fallback_secret", algorithm='HS256')
            response.set_cookie(key='Authorization', value=token, httponly=True, samesite=None)
            response.data = {"message":"login successful"}
            response.status_code = 200
        except Exception as e:
            print(str(e))
            response.data = {"message":"Internal server error, please try again after some time"}
            response.status_code = 500

        return response

class StudentLoginBypass(APIView):
    @ValidateSchema(StudentLoginBypassSchema)
    def post(self,request):
        roll_number = request.data['roll_number']
        institute_email = request.data['institute_email']
        response = Response()

        payload = {
            "institute_email":institute_email,
            "roll_number":roll_number,
            "exp": datetime.utcnow() + timedelta(days=2),
            "iat": datetime.utcnow()
        }

        try:
            token = jwt.encode(payload, getenv("COOKIE_ENCRYPTION_SECRET") or "fallback_secret", algorithm='HS256')
            response.set_cookie(key='Authorization', value=token, httponly=True, samesite=None)
            response.data = {"message":"login successful"}
            response.status_code = 200
        except Exception as e:
            print(str(e))
            response.data = {"message":"Internal server error, please try again after some time"}
            response.status_code = 500

        return response



class StudentDepartmentData(APIView):
    @StudentValidator()
    def get(self,request):
        response = Response()
        try:
            department_data = DepartmentStudentsMapping.objects.filter(
                student=request.student
            )
        except Exception as e:
            print(str(e))
            response.data = {"message":"Internal server error"}
            response.status_code = 500
            return response

        department_data_list = []
        for obj in department_data:
            data_obj = {
                "department_name":obj.department.name,
                "allow_certificate_generation":obj.allow_certificate_generation
            }
            department_data_list.append(data_obj)

        response.data = department_data_list
        response.status_code = 200
        return response

class GenerateNoDueCertificate(APIView):

    @ValidateSchema(GenerateNoDueCertificateSchema)
    @StudentValidator()
    def post(self,request):
        department_id = request.data.get('department_id')
        response = Response()

        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            response.data = {"message":"Department not found, Invalid request"}
            response.status_code = 404
            return response
        except Exception as e:
            print(str(e))
            response.data = {"message":"Internal server error, Contact admin"}
            response.status_code = 500
            return response

        try:
            mapping = DepartmentStudentsMapping.objects.get(student=request.student, department=department)
        except DepartmentStudentsMapping.DoesNotExist as e:
            response.data = {"message":"You are not added to this department"}
            response.status_code = 401
            return response
        except Exception as e:
            print(str(e))
            response.data = {"message":"Internal server error, Contact admin"}
            response.status_code = 500
            return response

        if not mapping.allow_certificate_generation:
            response.data = {"message":"You are not allowed to auto-generate certificate yet, please contact admin"}
            response.status_code = 401
            return response

        # :TODO: Generate certificate

        response.data = {"message":"Your certificate is being generated please check your vault"}
        response.status_code = 201
        return response
