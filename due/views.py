import traceback
from due.models import (
    Due,
    DueProofs,
    DueStatus,
    DueResponse,
    ResponseMode,
    ResponseStatus,
    ProcessDueResponseTypes,
)
from student.models import Student
from django.shortcuts import render
from django.core.serializers import serialize
from due.schema import (
    CreateDueSchema,
    CreateDueResponseSchema,
    ProcessDueRequestSchema
)
from utils.validator import ValidateSchema
from utils.auth import DepartmentValidator, StudentValidator
from rest_framework.views import APIView, Response
from utils.crypto import encode_cursor, decode_cursor
from django.db.models import Count
from django.db import transaction

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
        payment_url = request.data.get('payment_url')
        due_proofs = request.data.get('due_proofs')
        response = Response()

        if not due_proofs or len(due_proofs) == 0:
            print(due_proofs)
            response.data = {"message": "No due proof link, cannot create due"}
            response.status_code = 403
            return response

        if not payment_url:
            payment_url = request.department_user.department.default_payment_url

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
                status = DueStatus.PENDING.value,
                due_date = due_date,
                payment_url=payment_url
            )

            new_due.save()
            for link in due_proofs:
                try:
                    proof_obj = DueProofs.objects.create(
                        due = new_due,
                        proof_media_url = link
                    )
                    proof_obj.save()
                except Exception as e:
                    print(str(e))

            response.data = {
                "message":"Due successfully created",
                "data": {
                    "id": new_due.id,
                    "amount":new_due.amount,
                    "reason":new_due.reason,
                    "due_date":new_due.due_date,
                }
            }
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
                status= ResponseStatus.ON_HOLD.value
            )
            response.data = {"message": "response succesfully created"}
            response.status_code = 201
        except Exception as e:
            response.data = {"message":"Internal server error"}
            response.status_code = 500

        return response

class ProcessDueRequest(APIView):
    @DepartmentValidator()
    @ValidateSchema(ProcessDueRequestSchema)
    def post(self,request):
        due_request_id = request.data.get("due_request_id")
        response_status:ProcessDueResponseTypes = request.data.get("response")
        response = Response()

        try:
            due_response_instance = DueResponse.objects.get(id=due_request_id)
        except DueResponse.DoesNotExist as e:
            response.data = {"message":"Invalid due response id"}
            response.status_code = 404
            return response
        except Exception as e:
            response.data = {"message":"Internal server error"}
            response.status_code = 500
            return response

        if response_status == ProcessDueResponseTypes.REJECT.value:
            if due_response_instance.status == str(ResponseStatus.REJECTED):
                response.data = {"message":"Due request was already rejected"}
                response.status_code = 200
            else:
                try:
                    due_response_instance.status = ResponseStatus.REJECTED.value
                    due_response_instance.save()
                    response.data = {"message":"Due request rejected"}
                    response.status_code = 200
                except Exception as e:
                    response.data = {"message":"Internal server error"}
                    response.status_code = 500

            return response
        else:

            try:
                due_instance = Due.objects.get(id=due_response_instance.due.id)
            except Exception as e:
                response.data = {"message":"Due not found"}
                response.status_code = 404
                return response


            sid = transaction.savepoint()
            try:
                due_response_instance.status = ResponseStatus.ACCEPTED.value
                if due_response_instance.response_mode == ResponseMode.EXTERNAL_PAYMENT.value:
                    due_instance.status = DueStatus.PAID.value
                elif due_response_instance.response_mode == ResponseMode.REQUEST_CANCELLATION.value:
                    due_instance.status = DueStatus.CANCELLED.value
                due_instance.save()
                due_response_instance.save()
                transaction.savepoint_commit(sid)
                response.data = {"message":"Due request accepted"}
                response.status_code = 200
                return response
            except Exception as e:
                print(str(e))
                transaction.savepoint_rollback(sid)
                response.data = {"message":"Internal server error, Due request not accepted"}
                response.status_code = 500
                return response

