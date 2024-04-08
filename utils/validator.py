from pydantic import ValidationError
from rest_framework.response import Response
from json import loads

class ValidateSchema:
    def __init__(self, arg1):
        self.schema = arg1

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            validate = True
            try:
                request = args[1]
            except:
                validate = False

            if validate:
                try:
                    self.schema(**request.data)
                except ValidationError as e:
                    response = Response()
                    response.data = loads(e.json())
                    response.status_code = 403
                    return response
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                raise e
            return result
        return wrapper

class TemplateVariables:

    @classmethod
    def get_variable_data_from_mapping(cls, mapping):
        return {
            "student_first_name": mapping.student.first_name,
            "student_last_name": mapping.student.last_name,
            "student_academic_program": mapping.student.academic_program,
            "student_institute_email": mapping.student.institute_email,
            "student_joining_year": mapping.student.joining_year,
            "student_leaving_year": mapping.student.leaving_year,
            "department_name": mapping.department.name,
            "department_email": mapping.department.email,
        }

    @classmethod
    def get_available_variables(cls):
        variables = [
            "student_first_name",
            "student_last_name",
            "student_academic_program",
            "student_institute_email",
            "student_joining_year",
            "student_leaving_year",
            "department_name",
            "department_email",
        ]

        data = []
        index = 1
        for variable in variables:
            data.append({
                "name": variable,
                "id":index
            })
            index += 1

        return data


    @classmethod
    def get_variables_from_student_and_department(cls,student,department):
        return {
            "student_first_name": student.first_name,
            "student_last_name": student.last_name,
            "student_academic_program": student.academic_program,
            "student_institute_email": student.institute_email,
            "student_joining_year": student.joining_year,
            "student_leaving_year": student.leaving_year,
            "department_name": department.name,
            "department_email": department.email,
        }
