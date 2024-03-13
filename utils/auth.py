import os
import jwt
from student.models import Student
from department.models import DepartmentUser
from rest_framework.response import Response

class DepartmentValidator:
    def __init__(self,*args,**kwargs):
        pass

    def __call__(self, func) :
        def wrapper(*args,**kwargs):
            response = Response()
            try:
                request = args[1]
            except:
                response.data ={"message":"Internal server error"}
                response.status_code = 500
                return response


            token = request.COOKIES.get('Authorization')

            if not token:
                response.data = {"message":"You are unauthenticated. Please log in first."}
                response.status_code=401
                return response


            try:
                payload = jwt.decode(token, os.getenv("COOKIE_ENCRYPTION_SECRET") or "fallback_secret", algorithms='HS256')
            except jwt.ExpiredSignatureError:
                response.data = {"message": "Your token is expired. Please login again."}
                response.status_code = 409
                return response

            try:
                department_user = DepartmentUser.objects.get(id=payload["id"])
                request.department_user = department_user
            except:
                response.data = {"message": "Invalid token."}
                response.status_code=409
                return response

            try:
                result = func(*args, **kwargs)
            except Exception as e:
                raise e
            return result

        return wrapper


class StudentValidator:
    def __init__(self,*args,**kwargs):
        pass

    def __call__(self,func):
        def wrapper(self,*args,**kwargs):
            response = Response()

            try:
                if len(args) == 1:
                    request = args[0]
                else:
                    request = args[1]
            except:
                response.data = {"message":"Internal server error"}
                response.status_code = 500
                return response


            token = request.COOKIES.get('Authorization')

            if not token:
                response.data = {"message":"You are unauthenticated. Please log in first."}
                response.status_code=401
                return response


            try:
                payload = jwt.decode(token, os.getenv("COOKIE_ENCRYPTION_SECRET") or "fallback_secret", algorithms='HS256')
            except jwt.ExpiredSignatureError:
                response.data = {"message": "Your token is expired. Please login again."}
                response.status_code = 409
                return response

            try:
                student = Student.objects.get(roll_number=payload["roll_number"])
                request.student = student
            except:
                response.data = {"message": "Invalid token."}
                response.status_code=409
                return response

            try:
                result = func(*args, **kwargs)
            except Exception as e:
                raise e
            return result
        return wrapper
