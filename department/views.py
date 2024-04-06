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
from due.models import (
    Due,
    DueProofs,
    DueResponse,
    ResponseStatus
)
from student.models import Student
from utils.auth import DepartmentValidator
from utils.misc import convert_human_readable_date_time
from utils.validator import ValidateSchema, TemplateVariables
from department.schema import (
    LoginSchema,
    AddStudentToDepartmentSchema,
    ToggleCertificateGenerationPermissionSchema,
    EditCertificateHTMLTemplateSchema
)
from django.db.models import Count
from django.core.serializers import serialize
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from department.models import Department

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
        response.data = {
            "message":"Login Succesful",
            "token":token
        }
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
                'id':obj.id,
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

class ToggleCertificateGenerationPermission(APIView):
    @ValidateSchema(ToggleCertificateGenerationPermissionSchema)
    @DepartmentValidator()
    def post(self,request):
        roll_number = request.data.get('roll_number')
        response = Response()

        try:
            student = Student.objects.get(roll_number=roll_number)
        except Student.DoesNotExist:
            response.data = {"message":"Student does not exist"}
            response.status_code = 404
            return response
        except Exception as e:
            print(str(e))
            response.data = {"message":"Internal server error"}
            response.status_code = 500
            return response

        try:
            mapping = DepartmentStudentsMapping.objects.get(
                student = student,
                department = request.department_user.department
            )
        except DepartmentStudentsMapping.DoesNotExist:
            response.data = {"message":"student does not exist in department"}
            response.status_code = 404
            return response
        except Exception as e:
            print(str(e))
            response.data = {"message":"Internal server error"}
            response.status_code = 500
            return response

        try:
            mapping.allow_certificate_generation = not mapping.allow_certificate_generation
            mapping.save()
            response.data = {
                "roll_number": mapping.student.roll_number,
                "allow_certificate_generation":mapping.allow_certificate_generation
            }
            response.status_code = 200
        except Exception as e:
            response.data = {"message":"Internal server error"}
            response.status_code = 500

        return response

class EditCertificateHTMLTemplate(APIView):
    @DepartmentValidator()
    def get(self,request):
        return HttpResponse(request.department_user.department.certificate_pdf_template)

    @DepartmentValidator()
    @ValidateSchema(EditCertificateHTMLTemplateSchema)
    def post(self,request):
        edited_template = request.data.get('html_content')
        response = Response()

        try:
            department_instance = Department.objects.get(id=request.department_user.department.id)
            department_instance.certificate_pdf_template = edited_template
            department_instance.save()
            response.data = {"message":"Succesfully edited template"}
            response.status_code = 200
        except Exception as e:
            response.data = {"message":"Internal server error, contact admin"}
            response.status_code = 500

        return response

class GetDueById(APIView):

    @DepartmentValidator()
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


def get_template_variables(request):
    if request.method == 'GET':
        return JsonResponse({"variables":TemplateVariables.get_available_variables()},status=200)
    else:
        return JsonResponse({"message":"This method is not allowed"},status=405)

class GetDepartmentRequests(APIView):
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
        created_at_gt = request.query_params.get('created_at_gt',None)
        created_at_lt = request.query_params.get('created_at_lt',None)
        status = request.query_params.get('status',ResponseStatus.ON_HOLD)

        filters['due__department__id'] = request.department_user.department.id
        filters['due__student__is_active'] = True

        if role:
            filters['due__student__role'] = role
        if academic_program:
            filters['due__student__academic_program'] = academic_program
        if created_at_gt:
            filters['created_at__gt'] = created_at_gt
        if created_at_lt:
            filters['created_at__lt'] = created_at_lt
        if created_at_gt:
            filters['created_at__gt'] = created_at_gt

        filters['status'] = status

        try:
            count_query = DueResponse.objects.filter(**filters).aggregate(total_size=Count('id'))
            total_size = count_query['total_size']

            query = DueResponse.objects.filter(**filters)[cursor:cursor+limit]
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