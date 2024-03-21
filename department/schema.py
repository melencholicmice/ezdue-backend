from pydantic import BaseModel

class LoginSchema(BaseModel):
    username:str
    password:str

class AddStudentToDepartmentSchema(BaseModel):
    roll_number:str

class ToggleCertificateGenerationPermissionSchema(BaseModel):
    roll_number:str

class EditCertificateHTMLTemplateSchema(BaseModel):
    html_content:str