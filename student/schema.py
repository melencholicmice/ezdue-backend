from pydantic import BaseModel

class StudentLoginSchema(BaseModel):
    access_code:str