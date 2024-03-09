from django.db import models
from core.db.timestamp_mixin import TimestampMixin

class Role(models.TextChoices):
    BTECH = "B.Tech"
    MTECH = "M.Tech"
    PHD = "Phd"


class Student(TimestampMixin):

    roll_number = models.CharField(max_length=8,primary_key=True)

    first_name = models.CharField(max_length=128)

    last_name = models.CharField(max_length=128)

    institute_email = models.EmailField(null=False)

    joining_year = models.SmallIntegerField(null=False)

    leaving_year = models.SmallIntegerField(null=True)

    role = models.CharField(max_length=16,choices=Role.choices)

    academic_program = models.CharField(max_length=256)

    is_active = models.BooleanField(default=True)

    deactivated_on = models.DateTimeField(null=True,default=None)

