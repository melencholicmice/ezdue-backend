from django.db import models
from uuid import uuid4
from core.db.timestamp_mixin import TimestampMixin
from student.models import Student
from utils.crypto import hash_password

class Department(TimestampMixin):

    id = models.UUIDField(primary_key=True, default=uuid4)

    name = models.CharField(max_length=128, null=False)

    email = models.EmailField(null=False)

    certificate_pdf_template = models.TextField(null=False)

    def __str__(self):
        return self.name


class DepartmentUser(TimestampMixin):

    id = models.UUIDField(primary_key=True, default=uuid4)

    username = models.CharField(max_length=128,null=False)

    email = models.EmailField(null=False)

    department = models.ForeignKey(
        Department,
        null=False,
        on_delete=models.CASCADE
    )

    password = models.CharField(max_length=256,null=False)

    is_active = models.BooleanField(default=True)

    deactivated_on = models.DateTimeField(null=True,default=None)

    def save(self,*args,**kwargs):
        if self.password:
            self.password = hash_password(self.password)
        super(DepartmentUser,self).save(*args,**kwargs)


class DepartmentStudentsMapping(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4)

    student = models.ForeignKey(
        Student,
        null=False,
        on_delete=models.CASCADE
    )

    department = models.ForeignKey(
        Department,
        null=False,
        on_delete=models.CASCADE
    )

    allow_certificate_generation = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.department.name} + {self.student.roll_number}"