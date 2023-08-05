"""api_exceptions.py
Defines some custom API exceptions for different status codes for use
with Django REST framework since I did not find any built-in thing that did this."""
from http import HTTPStatus
from rest_framework.exceptions import APIException


class BadRequestException(APIException):
    """Exception for the Bad Request status."""

    status_code = HTTPStatus.BAD_REQUEST
    default_detail = {"status": "error", "message": "Bad request."}


class NotFoundException(APIException):
    """Exception for the Not Found status."""

    status_code = HTTPStatus.NOT_FOUND
    default_detail = {
        "status": "error",
        "message": "The requested resource was not found.",
    }


class InternalServerErrorException(APIException):
    """Exception for the Internal Server Error status."""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    default_detail = {"status": "error", "message": "An internal server occurred."}
