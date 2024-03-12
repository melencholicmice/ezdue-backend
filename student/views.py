from os import getenv
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from student.msal_plugin import MsLoginPlugin
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from student.models import Student


# Create your views here.


class StudentLoginViews(View):
    def __init__(self) -> None:
        self.ms_plugin = MsLoginPlugin(
            client_id=getenv("MSAL_CLIENT_ID"),
            client_secret=getenv("MSAL_CLIENT_SECRET")
        )

    @csrf_exempt
    def get(self,request):
        url = self.ms_plugin.get_auth_url()

        return JsonResponse({
            "login_url":url
        })


class GetStudents(APIView):
    def get(self, request):
       
        students = Student.objects.all()

        """
       limit offset
       total count:no of entries , data , next or previoius pointer .....encode to string 
       
       limit (query parameters) , cursor (string encoded for offset)         """
        filters = {}
        for param in ['joining_year', 'leaving_year', 'role', 'academic_program', 'is_active']:
            value = request.query_params.get(param)
            if value:
                filters[param] = value
        students = students.filter(**filters)

        
        page_number = request.query_params.get('page', 1)
        paginator = Paginator(students, 10) 
        page_obj = paginator.get_page(page_number)

        
        data = []
        for student in page_obj.object_list:
            data.append({
                'roll_number': student.roll_number,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'joining_year': student.joining_year,
                'leaving_year': student.leaving_year,
                'role': student.role,
                'academic_program': student.academic_program,
                'is_active': student.is_active,
                'deactivated_on': student.deactivated_on.strftime("%Y-%m-%d %H:%M:%S") if student.deactivated_on else None
            })

        return Response(data, status=status.HTTP_200_OK)
