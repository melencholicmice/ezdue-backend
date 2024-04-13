import jwt
from os import getenv
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import HttpResponse
from student.msal_plugin import MsLoginPlugin
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from student.models import Student
from department.models import DepartmentStudentsMapping, Department
from utils.validator import ValidateSchema, TemplateVariables
from utils.auth import StudentValidator
from student.schema import (
    StudentLoginSchema,
    StudentLoginBypassSchema,
    GenerateNoDueCertificateSchema
)
from due.models import (
    DueResponse,
    DueStatus,
    DueProofs
)
from django.db.models import Count
from due.models import Due, DueStatus
from jinja2 import Template
from utils.misc import convert_human_readable_date_time

class StudentLogin(APIView):
    def __init__(self):
        self.ms_plugin = MsLoginPlugin(
            client_id=getenv("MSAL_CLIENT_ID"),
            client_secret=getenv("MSAL_CLIENT_SECRET")
        )

    def get(self,request):
        response = Response()
        token = request.headers.get('Authorization')
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
            response.data  = {
                "message":"Login successful.",
                "data":{
                    "program":student.academic_program,
                    "roll_number":student.roll_number,
                    "email":student.institute_email,
                    "joining_year":student.joining_year,
                    "role":student.role,
                },
                "full_name":student.first_name + " " + student.last_name,
            }
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
            response.set_cookie('Authorization',token)
            response.data = {
                "message":"login successful",
                "token":token
            }
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
            response.data = {
                "message":"login successful",
                "token":token
            }
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
            pending_dues = Due.objects.filter(
                student__roll_number = request.student.roll_number,
                department__id = obj.id,
                status=DueStatus.PENDING
            ).aggregate(total_size=Count('id'))
            print(pending_dues)

            data_obj = {
                "department_name":obj.department.name,
                "allow_certificate_generation":obj.allow_certificate_generation,
                "id":obj.department.id,
                "total_pending_dues":pending_dues['total_size']
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

        variable_data = {
            "student_first_name":mapping.student.first_name,
            "student_last_name":mapping.student.last_name,
            "student_academic_program":mapping.student.academic_program,
            "student_institute_email":mapping.student.institute_email,
            "student_joining_year":mapping.student.joining_year,
            "student_leaving_year":mapping.student.leaving_year,
            "department_name":mapping.department.name,
            "department_email":mapping.department.email,
        }

        template = Template(mapping.department.certificate_pdf_template)
        rendered_html = template.render(TemplateVariables.get_variable_data_from_mapping(mapping=mapping))

        return HttpResponse(rendered_html)

class StudentDues(APIView):

    @StudentValidator()
    def get(self,request):

        response = Response()
        filters = {}
        due_date = request.query_params.get('due_date', None)
        status = request.query_params.get('status', None)

        filters['student__roll_number'] = request.student.roll_number
        if due_date:
            filters['due_date'] = due_date
        if status:
            filters['status'] = status

        try:
            count_query = Due.objects.filter(**filters).aggregate(total_size=Count('id'))
            total_size = count_query['total_size']
            query = Due.objects.filter(**filters)
            print(query.query)
            data = []
        except Exception as e:
            print(str(e))
            response.data = {"message":"Internal server error"}
            response.status_code = 500
            return response

        for obj in query:
            request_sent = False
            resp = DueResponse.objects.filter(due=obj)
            if len(resp) > 0:
                request_sent = True

            data.append({
                'request_sent':request_sent,
                'department_name':obj.department.name,
                'id':obj.id,
                'amount':obj.amount,
                'due_date':obj.due_date,
                'roll_number':obj.student.roll_number,
                'status':obj.status,
                'reason':obj.reason,
                'created_at':obj.created_at,
            })

        response.data = {
            "total": total_size,
            "data": data
        }
        response.status_code = 200
        return response

class GetStudentRequests(APIView):

    @StudentValidator()
    def get(self,request):
        response = Response()
        filters = {}


        status = request.query_params.get('status',None)
        if status:
            filters['status'] = status

        try:
            count_query = DueResponse.objects.filter(**filters).aggregate(total_size=Count('id'))
            total_size = count_query['total_size']

            query = DueResponse.objects.filter(**filters)
            print(query.query)
            data = []
        except Exception as e:
            print(str(e))
            response.data = {"message":"Internal server error"}
            response.status_code = 500
            return response

        for obj in query:
            data.append({
                'id': obj.id,
                'due_id':obj.due.id,
                'due_amount':obj.due.amount,
                'due_reason':obj.due.reason,
                'student_name': obj.due.student.first_name + " " + obj.due.student.last_name,
                'academic_program': obj.due.student.academic_program,
                'role': obj.due.student.role,
                'student_roll_number': obj.due.student.roll_number,
                'response_mode': obj.response_mode,
                'status': obj.status,
                'created_at': convert_human_readable_date_time(obj.created_at),
                'cancellation_reason':obj.cancellation_reason,
                'payment_proof_file':obj.payment_proof_file,
            })

        response.data = {
            "total": total_size,
            "data": data,
        }
        response.status_code = 200
        return response

class GetDueById(APIView):

    @StudentValidator()
    def get(self, request, due_id, format = None):
        response = Response()
        try:
            due_obj = Due.objects.get(id=due_id)
        except Due.DoesNotExist as e:
            response.data = {"message":"this due does not exists"}
            response.status_code = 404
            return response
        except Exception as e:
            print(str(e))
            response.data = {"message":"Internal server error, contact admin"}
            response.status_code = 500
            return response

        try:
            due_proofs = DueProofs.objects.filter(due=due_obj)
        except Exception as e:
            print(str(e))
            response.data = {"message":"Internal server error, contact admin"}
            response.status_code = 500
            return response

        due_proof_list = []

        for proof in due_proofs:
            due_proof_list.append(proof.proof_media_url)

        response.data  = {
            'id' : due_obj.id,
            'amount': due_obj.amount,
            'department' : due_obj.department.name,
            'due_date': convert_human_readable_date_time(due_obj.due_date),
            'proof': due_proof_list,
            'reason': due_obj.reason,
            'created_at': convert_human_readable_date_time(due_obj.created_at),
            'payment_url':due_obj.payment_url,
            'status': due_obj.status,
            'student_roll_number':due_obj.student.roll_number,
            'student_name': due_obj.student.first_name + " " + due_obj.student.last_name
        }
        response.status_code = 200

        return response