from rest_framework.response import Response

from apps.common.log_utils import render_error


class APIRequestError(Exception):
    def __init__(self, message: str = None, caused_by: Exception = None, http_status_code: int = 400) -> None:
        super().__init__(message)
        self.http_status_code = http_status_code
        self.message = message
        if caused_by:
            self.details = render_error(message, caused_by)
        else:
            self.details = None

    def to_frontend_error(self):
        return {
            'error': self.__class__.__name__,
            'message': self.message,
            'details': self.details
        }

    def to_response(self):
        return Response(data=self.to_frontend_error(), status=self.http_status_code)
