from django.urls import path
from due.views import (
    CreateDue,
    CreateDueResponse,
)

due_endpoints = [
    path("", CreateDue.as_view(), name="Create Due"),
    path("response", CreateDueResponse.as_view(), name="Create Due Response")
]
