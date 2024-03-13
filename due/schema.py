from uuid import UUID
from datetime import datetime
from due.models import ResponseStatus, ResponseMode
from pydantic import BaseModel, validator

class CreateDueSchema(BaseModel):
    student_rollnumber:str
    amount:int
    reason:str
    due_date: datetime

class CreateDueResponseSchema(BaseModel):
    due_id: str
    payment_proof_file: str
    cancellation_reason: str
    mode: ResponseMode

    @validator("mode")
    def check_mode(cls, v):
        if v == ResponseMode.PORTAL_PAYMENT:
            raise ValueError("This response mode is not allowed")
        return v

    