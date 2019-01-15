from apps.common.errors import APIRequestError


class Forbidden(APIRequestError):
    def __init__(self, message: str = None, caused_by: Exception = None) -> None:
        super().__init__(message, caused_by, http_status_code=403)


class FilterSyntaxError(APIRequestError):
    def __init__(self, message: str = None, caused_by: Exception = None, http_status_code: int = 400) -> None:
        super().__init__(message, caused_by, http_status_code)


class FilterValueParsingError(APIRequestError):
    def __init__(self, message: str = None, caused_by: Exception = None, http_status_code: int = 400) -> None:
        super().__init__(message, caused_by, http_status_code)


class OrderByParsingError(APIRequestError):
    def __init__(self, message: str = None, caused_by: Exception = None, http_status_code: int = 400) -> None:
        super().__init__(message, caused_by, http_status_code)


class UnknownColumnError(APIRequestError):
    def __init__(self, message: str = None, caused_by: Exception = None, http_status_code: int = 400) -> None:
        super().__init__(message, caused_by, http_status_code)
