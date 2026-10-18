"""CLI-утилита «Сводка по городу»."""

import argparse
import json
import re
import sys
from typing import Any

from clients.exceptions import ExternalServiceError, NotFoundError
from processing.service import build_city_summary


def city_argument(value: str) -> str:
    city = value.strip()
    if not city:
        raise argparse.ArgumentTypeError("название города не должно быть пустым")
    return city


def currency_argument(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z]{3}", value):
        raise argparse.ArgumentTypeError(
            "код валюты должен состоять из трёх латинских букв"
        )
    return value.upper()


def format_summary(summary: dict[str, Any]) -> str:
    weather = summary["weather"]
    rates = summary["rates"]
    return "\n".join(
        [
            f"Город: {summary['city']}",
            f"Погода: {weather['temp_c']:.1f}°C, {weather['description']}",
            f"Тёплая одежда: {'да' if weather['warm_clothes'] else 'нет'}",
            f"{rates['currency']}→RUB: {rates['rate_to_rub']:.2f}",
            f"Дорогой курс: {'да' if rates['expensive'] else 'нет'}",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Погода в городе и курс валюты к рублю."
    )
    parser.add_argument(
        "--city", required=True, type=city_argument, help="название города"
    )
    parser.add_argument(
        "--currency", default="USD", type=currency_argument, help="ISO-код валюты (USD)"
    )
    parser.add_argument(
        "--json", action="store_true", help="вывести сводку в формате JSON"
    )
    args = parser.parse_args(argv)

    try:
        summary = build_city_summary(args.city, args.currency)
    except NotFoundError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 3
    except ExternalServiceError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 4

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False))
    else:
        print(format_summary(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
