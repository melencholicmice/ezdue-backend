from pydantic import BaseModel

class StudentLoginSchema(BaseModel):
    access_code:str

class StudentLoginBypassSchema(BaseModel):
    roll_number:str
    institute_email:str