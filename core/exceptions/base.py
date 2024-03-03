from http import HTTPStatus


class UnimplementedError(Exception):
    error_code = HTTPStatus.INTERNAL_SERVER_ERROR
    message = "This feature is not yet implemented"

    def __init__(self, message=None) -> None:
        if message:
            self.message = message

