"""Общий GET с таймаутом, повторами и проверкой JSON."""

import math
import time
from typing import Any

import requests

from clients.exceptions import (
    ExternalServiceError,
    HTTPStatusError,
    InvalidResponseError,
)

TIMEOUT = 10  # Таймаут каждого запроса в секундах.
RETRY_STATUSES = {500, 502, 503, 504}
RETRIES = 3  # Три повтора после первой попытки: всего четыре запроса.
BACKOFF = 1


def _retry_delay(response: requests.Response, attempt: int) -> float:
    if response.status_code == 429:
        try:
            delay = float(response.headers.get("Retry-After", ""))
        except ValueError:
            pass
        else:
            if math.isfinite(delay) and delay >= 0:
                return delay
    return BACKOFF * 2**attempt


def get_json(url: str, params: dict[str, Any] | None = None) -> Any:
    """Выполнить GET; ошибки сети и ответа преобразовать в ошибки приложения."""
    for attempt in range(RETRIES + 1):
        try:
            response = requests.get(url, params=params, timeout=TIMEOUT)
        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ) as exc:
            if attempt == RETRIES:
                raise ExternalServiceError(
                    f"Сервис {url} недоступен после {RETRIES + 1} попыток."
                ) from exc
            time.sleep(BACKOFF * 2**attempt)
            continue
        except requests.exceptions.RequestException as exc:
            raise ExternalServiceError(f"Не удалось выполнить запрос к {url}.") from exc

        try:
            if response.status_code in RETRY_STATUSES or response.status_code == 429:
                if attempt == RETRIES:
                    raise HTTPStatusError(response.status_code, url)
                delay = _retry_delay(response, attempt)
            elif not 200 <= response.status_code < 300:
                raise HTTPStatusError(response.status_code, url)
            else:
                try:
                    return response.json()
                except ValueError as exc:
                    raise InvalidResponseError(
                        f"Сервис {url} вернул некорректный JSON."
                    ) from exc
        finally:
            response.close()

        time.sleep(delay)
