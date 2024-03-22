from django.urls import path
from due.views import (
    CreateDue,
    CreateDueResponse,
    ProcessDueRequest
)

due_endpoints = [
    path("", CreateDue.as_view(), name="Create Due"),
    path("response", CreateDueResponse.as_view(), name="Create Due Response"),
    path("process-response", ProcessDueRequest.as_view(), name="Process Due Response")
]
