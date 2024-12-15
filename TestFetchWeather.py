import unittest
from unittest.mock import patch, mock_open
import requests
from datetime import datetime
import json

# Импортируем тестируемую функцию
from Weather_logger import fetch_weather

# Создаем класс для тестов, наследующийся от unittest.TestCase
class TestWeatherLogger(unittest.TestCase):

    # Тест успешного выполнения функции fetch_weather
    @patch("Weather_logger.requests.get")  # Мокаем функцию requests.get для подмены HTTP-запросов
    @patch("builtins.open", new_callable=mock_open)  # Мокаем функцию open для подмены работы с файлами
    def test_fetch_weather_success(self, mock_file, mock_get):
        # Создаем фейковый ответ от API, который будет возвращаться при вызове requests.get
        mock_response = {
            "name": "TestCity",  # Название города
            "main": {"temp": 25.3}  # Температура в формате API
        }
        mock_get.return_value.status_code = 200  # Указываем, что запрос завершился успешно
        mock_get.return_value.json.return_value = mock_response  # Указываем, какой JSON возвращает запрос

        # Ожидаемое содержимое записи в файл
        expected_log_entry = {
            "city": "TestCity",  # Название города
            "temperature": 25,  # Округленная температура
            "timestamp": datetime.now().isoformat()  # Временная метка
        }

        # Мокаем datetime для фиксации времени
        with patch("Weather_logger.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)  # Фиксируем дату и время
            expected_log_entry["timestamp"] = "2023-01-01T12:00:00"  # Обновляем ожидаемую временную метку
            fetch_weather()  # Запускаем тестируемую функцию

        # Проверяем, что запрос к API был выполнен с ожидаемыми параметрами
        mock_get.assert_called_once_with(
            "https://api.openweathermap.org/data/2.5/weather",  # URL API
            params={  # Параметры запроса
                "q": "TestCity",  # Название города
                "appid": "d7268901c56fc9ce3a71ead8a4dbff42",  # API-ключ
                "units": "metric"  # Единицы измерения температуры (градусы Цельсия)
            }
        )

        # Проверяем, что данные были записаны в файл
        mock_file().write.assert_called_once_with(json.dumps(expected_log_entry) + "\n")

    # Тест обработки ошибки HTTP-запроса
    @patch("Weather_Logger.requests.get")  # Мокаем requests.get
    def test_fetch_weather_http_error(self, mock_get):
        # Настраиваем mock для возврата исключения при выполнении HTTP-запроса
        mock_get.side_effect = requests.exceptions.RequestException("HTTP Error")

        # Проверяем, что исключение обрабатывается корректно и записывается в лог
        with self.assertLogs("weather_logger.logging", level="ERROR") as log:
            fetch_weather()  # Запускаем тестируемую функцию

        # Проверяем, что лог содержит сообщение об ошибке
        self.assertIn("Error fetching weather data: HTTP Error", log.output[0])

    # Тест обработки ошибки записи в файл
    @patch("builtins.open", new_callable=mock_open)  # Мокаем функцию open
    @patch("Weather_Logger.requests.get")  # Мокаем requests.get
    def test_fetch_weather_file_write_error(self, mock_get, mock_file):
        # Создаем фейковый ответ от API
        mock_response = {
            "name": "TestCity",  # Название города
            "main": {"temp": 25.3}  # Температура
        }
        mock_get.return_value.status_code = 200  # Запрос успешен
        mock_get.return_value.json.return_value = mock_response  # Возвращаемый JSON-ответ

        # Настраиваем mock для вызова исключения при записи в файл
        mock_file.side_effect = IOError("File write error")

        # Проверяем, что исключение обрабатывается корректно и записывается в лог
        with self.assertLogs("weather_logger.logging", level="ERROR") as log:
            fetch_weather()  # Запускаем тестируемую функцию

        # Проверяем, что лог содержит сообщение об ошибке
        self.assertIn("Error fetching weather data", log.output[0])

# Точка входа для запуска тестов
if __name__ == "__main__":
    unittest.main()

