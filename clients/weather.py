"""Получение координат города и текущей погоды через Open-Meteo."""

import math
from typing import Any

from clients.exceptions import InvalidResponseError, NotFoundError
from clients.http import get_json

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_DESCRIPTIONS = {
    0: "ясно",
    1: "преимущественно ясно",
    2: "переменная облачность",
    3: "пасмурно",
    45: "туман",
    48: "туман с изморозью",
    51: "слабая морось",
    53: "умеренная морось",
    55: "сильная морось",
    56: "слабая переохлаждённая морось",
    57: "сильная переохлаждённая морось",
    61: "слабый дождь",
    63: "умеренный дождь",
    65: "сильный дождь",
    66: "слабый ледяной дождь",
    67: "сильный ледяной дождь",
    71: "слабый снег",
    73: "умеренный снег",
    75: "сильный снег",
    77: "снежные зёрна",
    80: "слабый ливень",
    81: "умеренный ливень",
    82: "сильный ливень",
    85: "слабый снежный ливень",
    86: "сильный снежный ливень",
    95: "гроза",
    96: "гроза со слабым градом",
    97: "сильная гроза",
    99: "гроза с сильным градом",
}


def _number(value: Any, field: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
    ):
        raise InvalidResponseError(f"Open-Meteo: некорректное поле {field}.")
    return float(value)


def get_weather(city: str) -> dict[str, Any]:
    """Вернуть температуру в °C и описание погоды для первого найденного города."""
    locations = get_json(
        GEOCODING_URL,
        params={"name": city, "count": 1, "language": "ru", "format": "json"},
    )
    if not isinstance(locations, dict) or locations.get("error"):
        raise InvalidResponseError("Open-Meteo: некорректный ответ геокодинга.")
    # При отсутствии совпадений Open-Meteo может не возвращать ключ results.
    results = locations.get("results", [])
    if not isinstance(results, list):
        raise InvalidResponseError("Open-Meteo: поле results должно быть списком.")
    if not results:
        raise NotFoundError(f"Город «{city}» не найден.")
    location = results[0]
    if not isinstance(location, dict):
        raise InvalidResponseError("Open-Meteo: некорректные данные города.")
    latitude = _number(location.get("latitude"), "latitude")
    longitude = _number(location.get("longitude"), "longitude")
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise InvalidResponseError(
            "Open-Meteo: координаты города вне допустимого диапазона."
        )

    data = get_json(
        WEATHER_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,weather_code",
            "temperature_unit": "celsius",
        },
    )
    if not isinstance(data, dict) or data.get("error"):
        raise InvalidResponseError("Open-Meteo: некорректный ответ погоды.")
    current = data.get("current")
    if not isinstance(current, dict):
        raise InvalidResponseError("Open-Meteo: отсутствует объект current.")
    temperature = _number(current.get("temperature_2m"), "temperature_2m")
    code = current.get("weather_code")
    if (
        isinstance(code, bool)
        or not isinstance(code, int)
        or code not in WEATHER_DESCRIPTIONS
    ):
        raise InvalidResponseError("Open-Meteo: некорректный код погоды.")
    return {"temp_c": temperature, "description": WEATHER_DESCRIPTIONS[code]}
