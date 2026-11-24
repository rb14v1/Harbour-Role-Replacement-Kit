from pymongo.errors import PyMongoError
from rest_framework.response import Response


class AppError(Exception):
    def __init__(self, message, code="error", status_code=400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


def error_response(message, code, status_code, details=None):
    body = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return Response(body, status=status_code)


def custom_exception_handler(exc, context):
    from rest_framework.views import exception_handler

    if isinstance(exc, AppError):
        return error_response(exc.message, exc.code, exc.status_code)
    if isinstance(exc, PyMongoError):
        return error_response(
            "The database is unavailable. Check that MongoDB is running and try again.",
            "database_unavailable",
            503,
        )
    response = exception_handler(exc, context)
    if response is None:
        return error_response("Something went wrong on the server. Try again.", "server_error", 500)
    data = response.data
    if isinstance(data, dict) and "detail" in data:
        return error_response(str(data["detail"]), getattr(exc, "default_code", "error"), response.status_code)
    return error_response(
        "Please correct the highlighted fields and try again.",
        "validation_error",
        response.status_code,
        details=data,
    )
