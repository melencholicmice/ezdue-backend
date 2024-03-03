from os import getenv
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from student.msal_plugin import MsLoginPlugin
from django.views import View
from django.views.decorators.csrf import csrf_exempt

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