import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from main import main
from processing.preprocessing import preprocess_rate, preprocess_weather
from processing.service import build_city_summary


class SummaryTests(unittest.TestCase):
    def test_warm_clothes(self):
        weather = {"temp_c": -3.2, "description": "ясно"}
        self.assertTrue(preprocess_weather(weather)["warm_clothes"])

    def test_expensive_rate(self):
        self.assertTrue(preprocess_rate("USD", 101.5)["expensive"])

    @patch("processing.service.get_rate", return_value=92.15)
    @patch(
        "processing.service.get_weather",
        return_value={"temp_c": -3.2, "description": "ясно"},
    )
    def test_build_summary(self, weather, rate):
        summary = build_city_summary("Moscow")
        self.assertEqual(
            summary,
            {
                "city": "Moscow",
                "weather": {
                    "temp_c": -3.2,
                    "description": "ясно",
                    "warm_clothes": True,
                },
                "rates": {"currency": "USD", "rate_to_rub": 92.15, "expensive": False},
            },
        )

    @patch("processing.service.get_rate", return_value=92.15)
    @patch(
        "processing.service.get_weather",
        return_value={"temp_c": -3.2, "description": "ясно"},
    )
    def test_cli_output(self, weather, rate):
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--city", "Moscow"])
        self.assertEqual(code, 0)
        self.assertIn("Город: Moscow", output.getvalue())
        self.assertIn("USD→RUB: 92.15", output.getvalue())
