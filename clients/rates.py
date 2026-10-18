"""Курс выбранной валюты к рублю через Frankfurter v2."""

import math
import re
from datetime import date

from clients.exceptions import HTTPStatusError, InvalidResponseError, NotFoundError
from clients.http import get_json

RATE_URL = "https://api.frankfurter.dev/v2/rate/{currency}/RUB"


def get_rate(currency: str = "USD") -> float:
    """Вернуть стоимость одной единицы валюты в рублях."""
    currency = currency.strip().upper()
    if not re.fullmatch(r"[A-Z]{3}", currency):
        raise NotFoundError(f"Код валюты «{currency}» не найден.")
    if currency == "RUB":
        return 1.0

    try:
        data = get_json(RATE_URL.format(currency=currency))
    except HTTPStatusError as exc:
        # В v2 неизвестная валюта возвращает 422, отсутствующий курс - 404.
        if exc.status_code in {404, 422}:
            raise NotFoundError(
                f"Валюта «{currency}» или её курс к RUB не найдены."
            ) from exc
        raise

    if not isinstance(data, dict):
        raise InvalidResponseError("Frankfurter: ожидался JSON-объект.")
    if data.get("base") != currency or data.get("quote") != "RUB":
        raise InvalidResponseError("Frankfurter: неверная валютная пара в ответе.")
    try:
        date.fromisoformat(data["date"])
    except (KeyError, TypeError, ValueError) as exc:
        raise InvalidResponseError(
            "Frankfurter: отсутствует или некорректна дата курса."
        ) from exc

    rate = data.get("rate")
    if (
        isinstance(rate, bool)
        or not isinstance(rate, (int, float))
        or not math.isfinite(rate)
        or rate <= 0
    ):
        raise InvalidResponseError(
            "Frankfurter: курс должен быть положительным числом."
        )
    return float(rate)
