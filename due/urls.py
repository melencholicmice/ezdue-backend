from django.urls import path
from due.views import CreateDue
due_endpoints = [
    path("", CreateDue.as_view(), name="Create Due")
]