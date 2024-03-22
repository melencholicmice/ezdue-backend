from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, validator, HttpUrl, Field
from due.models import ResponseStatus, ResponseMode, ProcessDueResponseTypes

class CreateDueSchema(BaseModel):
    student_rollnumber:str
    amount:int
    reason:str
    due_date: datetime
    payment_url: Optional[HttpUrl] = Field(default=None)

class CreateDueResponseSchema(BaseModel):
    due_id: UUID
    payment_proof_file: Optional[HttpUrl] = Field(default=None)
    cancellation_reason: Optional[str] = Field(default=None)
    mode: ResponseMode

    @validator("mode")
    def check_mode(cls, v, values, **kwargs):
        payment_proof_file = values.get("payment_proof_file")
        cancellation_reason = values.get("cancellation_reason")

        if v == ResponseMode.PORTAL_PAYMENT:
            raise ValueError("This response mode is not allowed")
        if v == ResponseMode.EXTERNAL_PAYMENT:
            if payment_proof_file is None:
                raise ValueError("payment proof file is required")
            if cancellation_reason is not None:
                raise ValueError("cancellation reason is not allowed in external payment")
        if v == ResponseMode.REQUEST_CANCELLATION:
            if payment_proof_file is not None:
                raise ValueError("payment proof file is not required here")
            if cancellation_reason is None:
                raise ValueError("cancellation reason is required in cancellation request")
        return v

class ProcessDueRequestSchema(BaseModel):
    due_request_id:UUID
    response: ProcessDueResponseTypes