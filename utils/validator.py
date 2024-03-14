from pydantic import ValidationError
from rest_framework.response import Response
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
                    response.data = {
                        "error_count": e.error_count(),
                        "error":e.json()
                    }
                    response.status_code = 403
                    return response
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                raise e
            return result
        return wrapper