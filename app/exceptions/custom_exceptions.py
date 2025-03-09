# File: app/exceptions/custom_exceptions.py

from fastapi import HTTPException, status

class BaseAppException(HTTPException):
    """
    Базовый класс для всех кастомных исключений приложения.
    Позволяет задавать статус, сообщение об ошибке и дополнительную информацию.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Internal Server Error"

    def __init__(self, detail: str = None):
        if detail:
            self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)

# -------------------------
# Исключения, связанные с пользователями
# -------------------------
class UserAlreadyExistsException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже существует"

class UserNotFoundException(BaseAppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Пользователь не найден"

# -------------------------
# Исключения, связанные с фильмами
# -------------------------
class MovieNotFoundException(BaseAppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Фильм не найден"

class MovieValidationException(BaseAppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Ошибка валидации данных фильма"

class InvalidRatingException(BaseAppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Неверное значение рейтинга. Рейтинг должен быть в диапазоне от 0 до 10"

class InvalidDurationException(BaseAppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Неверная продолжительность фильма. Продолжительность не может быть отрицательной"

class DuplicateMovieException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Фильм с такими данными уже существует"

# -------------------------
# Исключения, связанные с подписками
# -------------------------
class SubscriptionNotFoundException(BaseAppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Подписка не найдена"

class SubscriptionConflictException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "У вас уже есть активная подписка"

class InvalidSubscriptionDatesException(BaseAppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Неверные даты подписки. Дата окончания не может быть раньше даты начала"

# -------------------------
# Исключения, связанные с платежами
# -------------------------
class PaymentNotFoundException(BaseAppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Платёж не найден"

class PaymentProcessingException(BaseAppException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Ошибка обработки платежа"

# -------------------------
# Исключения, связанные с отзывами
# -------------------------
class ReviewNotFoundException(BaseAppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Отзыв не найден"

# -------------------------
# Общие исключения валидации и входных данных
# -------------------------
class InvalidInputException(BaseAppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Некорректные входные данные"

class InvalidDateFormatException(BaseAppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Неверный формат даты. Ожидается ISO формат, например: 2020-01-01T00:00:00Z"

class NoUpdateDataException(BaseAppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Нет данных для обновления"

class IncompleteDataException(BaseAppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Неполные данные запроса. Проверьте обязательные поля"

class ParsingException(BaseAppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Ошибка при разборе данных запроса"

# -------------------------
# Исключения, связанные с аутентификацией и авторизацией
# -------------------------
class AuthenticationException(BaseAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Ошибка аутентификации. Неверные учетные данные"

class AccessDeniedException(BaseAppException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Доступ запрещён"

class TokenExpiredException(BaseAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен истёк. Пожалуйста, авторизуйтесь снова"

class InvalidTokenException(BaseAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный токен. Пожалуйста, проверьте данные авторизации"

# -------------------------
# Исключения, связанные с подтверждением возраста и подписками
# -------------------------
class AgeNotConfirmedException(BaseAppException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Для просмотра данного контента необходимо подтвердить, что вам 18+"

class AgeConfirmationExpiredException(BaseAppException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Подтверждение возраста истекло. Повторите подтверждение"

class SubscriptionRequiredException(BaseAppException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Для доступа к этому контенту требуется активная подписка"

# -------------------------
# Исключения, связанные с внешними сервисами и API
# -------------------------
class StripeWebhookException(BaseAppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Ошибка при обработке вебхука Stripe"

class ExternalServiceUnavailableException(BaseAppException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Внешний сервис временно недоступен. Попробуйте повторить запрос позже"

class ExternalAPIErrorException(BaseAppException):
    status_code = status.HTTP_502_BAD_GATEWAY
    detail = "Ошибка при взаимодействии с внешним API"

# -------------------------
# Исключения, связанные с потоковым воспроизведением
# -------------------------
class StreamingUnavailableException(BaseAppException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Сервис потокового воспроизведения временно недоступен"

# -------------------------
# Прочие исключения
# -------------------------
class RateLimitExceededException(BaseAppException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Превышен лимит запросов. Попробуйте позже"

class RequestTimeoutException(BaseAppException):
    status_code = status.HTTP_408_REQUEST_TIMEOUT
    detail = "Время ожидания запроса истекло. Попробуйте снова"
