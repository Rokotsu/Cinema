# File: app/exceptions/custom_exceptions.py
from fastapi import HTTPException, status

class BaseAppException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Internal Server Error"

    def __init__(self, detail: str = None):
        if detail:
            self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)

class UserAlreadyExistsException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже существует"

class UserNotFoundException(BaseAppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Пользователь не найден"

class MovieNotFoundException(BaseAppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Фильм не найден"

class SubscriptionNotFoundException(BaseAppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Подписка не найдена"

class PaymentNotFoundException(BaseAppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Платёж не найден"

class PaymentProcessingException(BaseAppException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Ошибка обработки платежа"

class ReviewNotFoundException(BaseAppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Отзыв не найден"
