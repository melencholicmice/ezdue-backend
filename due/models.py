from enum import Enum
from django.db import models
from uuid import uuid4
from core.db.timestamp_mixin import TimestampMixin
from student.models import Student
from department.models import Department

class ResponseMode(Enum):
    REQUEST_CANCELLATION = "request cancellation"
    PORTAL_PAYMENT = "portal payment"
    EXTERNAL_PAYMENT = "external payment"

class DueStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"

class ResponseStatus(Enum):
    ON_HOLD = "on hold"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class Due(TimestampMixin):

    id = models.UUIDField(primary_key=True, default=uuid4)

    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    amount = models.PositiveIntegerField(null=False)

    reason = models.TextField(null=False)

    status = models.CharField(max_length=16, choices=[(status.value, status.name) for status in DueStatus])

    due_date = models.DateTimeField(null=False)


class DueResponse(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4)

    due = models.ForeignKey(Due, on_delete=models.CASCADE)

    response_mode = models.CharField(max_length=32, choices=[(mode.value, mode.name) for mode in ResponseMode])

    payment_proof_file = models.URLField(null=True,default=None)

    cancellation_reason = models.TextField(null=True, default=None)

    status = models.CharField(max_length=16, choices=[(status.value, status.name) for status in ResponseStatus])


class RazorpayPayments(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4)

    due_response = models.ForeignKey(DueResponse, on_delete=models.CASCADE)