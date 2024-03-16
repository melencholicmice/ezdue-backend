import traceback
from due.models import Due, DueStatus, DueResponse, ResponseStatus
from student.models import Student
from django.shortcuts import render
from django.core.serializers import serialize
from due.schema import CreateDueSchema, CreateDueResponseSchema
from utils.validator import ValidateSchema
from utils.auth import DepartmentValidator, StudentValidator
from rest_framework.views import APIView, Response
from utils.crypto import encode_cursor, decode_cursor
from django.db.models import Count

class CreateDue(APIView):
    @ValidateSchema(CreateDueSchema)
    @DepartmentValidator()
    def post(
        self,
        request
    ):
        student_rollnumber = request.data["student_rollnumber"].lower()
        department = request.department_user.department
        amount = request.data["amount"]
        reason = request.data["reason"]
        due_date = request.data["due_date"]
        response = Response()

        try:
            student = Student.objects.get(roll_number=student_rollnumber)
        except Student.DoesNotExist:
            response.data = {"message": f"student does not exist with rollnumber {student_rollnumber}"}
            response.status_code = 404
            return response
        except Exception as e:
            print(str(e))
            response.data = {"message": "some error occured while verifying student, Please try again"}
            response.status_code = 500
            return response


        try:
            new_due = Due.objects.create(
                student = student,
                department = department,
                amount = amount,
                reason = reason,
                status = DueStatus.PENDING,
                due_date = due_date
            )

            new_due.save()
            response.data = {"message":"Due successfully created"}
            response.status_code = 201
        except Exception as e:
            print(f"{str(e)}\n{traceback.format_exception(e)}")
            response.data = {"message": "some error occured, Please try again"}
            response.status_code = 500


        return response



class CreateDueResponse(APIView):

    @ValidateSchema(CreateDueResponseSchema)
    @StudentValidator()
    def post(self,request):
        due_id = request.data['due_id']
        student_instance = request.student
        response_mode = request.data['mode']
        payment_proof_file = request.data.get('payment_proof_file') or None
        cancellation_reason = request.data.get('cancellation_reason') or None

        response = Response()

        try:
            due_instance = Due.objects.get(id = due_id, student = student_instance)
        except Due.DoesNotExist as e:
            response.data = {"message":"No such due exist for the user"}
            response.status_code = 404
            return response
        except Exception as e:
            response.data = {"message":"Internal server error"}
            response.status_code = 500
            return response

        try:
            due_response = DueResponse.objects.create(
                due=due_instance,
                response_mode=response_mode,
                payment_proof_file=payment_proof_file,
                cancellation_reason=cancellation_reason,
                status=ResponseStatus.ON_HOLD
            )
            response.data = {"message": "response succesfully created"}
            response.status_code = 201
        except Exception as e:
            response.data = {"message":"Internal server error"}
            response.status_code = 500

        return response
