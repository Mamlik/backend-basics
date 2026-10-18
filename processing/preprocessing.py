"""Правила предобработки данных; здесь нет HTTP-запросов и вывода."""

from typing import Any


def preprocess_weather(weather: dict[str, Any]) -> dict[str, Any]:
    """Добавить совет о тёплой одежде, не изменяя исходный словарь."""
    return {**weather, "warm_clothes": weather["temp_c"] < 0}


def preprocess_rate(currency: str, rate: float) -> dict[str, Any]:
    """Отметить курс выше 100 рублей за единицу валюты как дорогой."""
    return {"currency": currency, "rate_to_rub": rate, "expensive": rate > 100}
