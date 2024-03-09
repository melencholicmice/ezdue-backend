import os
import jwt
import datetime
from django.shortcuts import render
from utils.crypto import verify_password
from department.models import DepartmentUser
from utils.auth import DepartmentValidator
from utils.validator import ValidateSchema
from department.schema import LoginSchema
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
            response.data = {"message":"Invalid credentials, user not found"}
            response.status_code = 404
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


