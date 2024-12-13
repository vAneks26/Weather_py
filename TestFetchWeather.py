import unittest
from unittest.mock import patch, mock_open
import requests
from datetime import datetime
import json

# Импортируем тестируемую функцию
from Weather_logger import fetch_weather

class TestWeatherLogger(unittest.TestCase):

    @patch("Weather_logger.requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_fetch_weather_success(self, mock_file, mock_get):
        # Создаем фейковый ответ от API
        mock_response = {
            "name": "TestCity",
            "main": {"temp": 25.3}
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        # Ожидаемое содержимое записи
        expected_log_entry = {
            "city": "TestCity",
            "temperature": 25,
            "timestamp": datetime.now().isoformat()
        }

        # Запускаем функцию
        with patch("Weather_logger.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
            expected_log_entry["timestamp"] = "2023-01-01T12:00:00"
            fetch_weather()

        # Проверяем, что запрос был выполнен с правильными параметрами
        mock_get.assert_called_once_with(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": "TestCity",
                "appid": "d7268901c56fc9ce3a71ead8a4dbff42",
                "units": "metric"
            }
        )

        # Проверяем, что данные были записаны в файл
        mock_file().write.assert_called_once_with(json.dumps(expected_log_entry) + "\n")

    @patch("Weather_Logger.requests.get")
    def test_fetch_weather_http_error(self, mock_get):
        # Настраиваем mock для возврата ошибки
        mock_get.side_effect = requests.exceptions.RequestException("HTTP Error")

        # Проверяем, что исключение обрабатывается корректно
        with self.assertLogs("weather_logger.logging", level="ERROR") as log:
            fetch_weather()

        # Проверяем, что лог содержит сообщение об ошибке
        self.assertIn("Error fetching weather data: HTTP Error", log.output[0])

    @patch("builtins.open", new_callable=mock_open)
    @patch("Weather_Logger.requests.get")
    def test_fetch_weather_file_write_error(self, mock_get, mock_file):
        # Создаем фейковый ответ от API
        mock_response = {
            "name": "TestCity",
            "main": {"temp": 25.3}
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        # Настраиваем mock для вызова ошибки при записи файла
        mock_file.side_effect = IOError("File write error")

        # Проверяем, что исключение обрабатывается корректно
        with self.assertLogs("weather_logger.logging", level="ERROR") as log:
            fetch_weather()

        # Проверяем, что лог содержит сообщение об ошибке
        self.assertIn("Error fetching weather data", log.output[0])

if __name__ == "__main__":
    unittest.main()

