import traceback
from due.models import Due
from due.models import DueStatus
from student.models import Student
from django.shortcuts import render
from due.schema import CreateDueSchema
from utils.validator import ValidateSchema
from utils.auth import DepartmentValidator
from rest_framework.views import APIView, Response

class CreateDue(APIView):
    @ValidateSchema(CreateDueSchema)
    @DepartmentValidator()
    def post(
        self,
        request
    ):
        student_rollnumber = request.data["student_rollnumber"]
        department = request.department_user.department
        amount = request.data["amount"]
        reason = request.data["reason"]
        due_date = request.data["due_date"]
        response = Response()

        try:
            student = Student.objects.get()
        except Student.DoesNotExist:
            response.data = {
                "message": f"student does not exist with rollnumber {student_rollnumber}"
            }
            response.status_code = 404
            return response
        except:
            response.data = {
                "message": "some error occured while verifying student, Please try again"
            }
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
            response.data = {
                "message":"Due successfully created"
            }
            response.status_code = 201
        except Exception as e:
            print(f"{str(e)}\n{traceback.format_exception(e)}")
            response.data = {
                "message": "some error occured, Please try again"
            }
            response.status_code = 500


        return response



