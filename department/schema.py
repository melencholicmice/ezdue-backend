from pydantic import BaseModel

class LoginSchema(BaseModel):
    username:str
    password:str

class AddStudentToDepartmentSchema(BaseModel):
    roll_number:str