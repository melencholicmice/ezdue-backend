from pydantic import BaseModel
from uuid import UUID

class StudentLoginSchema(BaseModel):
    access_code:str

class StudentLoginBypassSchema(BaseModel):
    roll_number:str
    institute_email:str

class GenerateNoDueCertificateSchema(BaseModel):
    department_id:UUID