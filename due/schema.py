from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class CreateDueSchema(BaseModel):
    student_rollnumber:str
    amount:int
    reason:str
    due_date: datetime
