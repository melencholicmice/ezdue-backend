import jwt
from os import getenv
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from student.msal_plugin import MsLoginPlugin
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from student.models import Student
from utils.validator import ValidateSchema
from student.schema import StudentLoginSchema

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
            except jwt.ExpiredSignatureError:
                pass

        if correct_token:
            response.data  = {"message":"Login successful"}
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

        if not self.ms_plugin.validate_profile_data(user_data=profile_data):
            response.data = {"message":"User not found in database, please contact admin"}
            response.status_code = 404
            return response

        response.data = profile_data
        response.status_code = 200
        return response


