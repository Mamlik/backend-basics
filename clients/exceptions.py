"""Ошибки приложения, не зависящие от библиотеки requests."""


class NotFoundError(Exception):
    """Город или валюта не найдены."""


class ExternalServiceError(Exception):
    """Не удалось получить данные внешнего сервиса."""


class InvalidResponseError(ExternalServiceError):
    """Сервис вернул некорректные данные."""


class HTTPStatusError(ExternalServiceError):
    """HTTP-ошибка, которую клиент может перевести в ошибку предметной области."""

    def __init__(self, status_code: int, url: str) -> None:
        self.status_code = status_code
        super().__init__(f"Сервис {url} вернул HTTP {status_code}.")
