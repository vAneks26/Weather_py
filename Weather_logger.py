import requests
import json
from datetime import datetime
import schedule
import time
import logging

# Настройка логирования
LOG_FILE = "weather_log.txt"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# URL API сервиса погоды OpenWeather
API_URL = "https://api.openweathermap.org/data/2.5/weather"

# Ваш API-ключ для доступа к OpenWeather
API_KEY = "d7268901c56fc9ce3a71ead8a4dbff42"

# Город, для которого запрашиваем погоду
CITY = input("Введите название города: ")

# Путь к файлу, в который будем записывать данные
FILE_PATH = "weather_data.json"

def fetch_weather():
    """
    Получает данные о погоде с сайта OpenWeather и записывает город, температуру и время в файл.
    """
    try:
        # Параметры запроса к API
        params = {
            "q": CITY,          # Название города
            "appid": API_KEY,   # Ваш API-ключ
            "units": "metric",  # Единицы измерения (градусы Цельсия)
        }

        # Выполняем HTTP GET-запрос к API
        response = requests.get(API_URL, params=params)

        # Если произошла ошибка, выбрасываем исключение
        response.raise_for_status()

        # Преобразуем ответ в формате JSON в Python-словарь
        weather_data = response.json()

        # Подготавливаем данные для записи
        log_entry = {
            "city": weather_data["name"],
            "temperature": round(weather_data["main"]["temp"]),
            "timestamp": datetime.now().isoformat()
        }

        # Открываем файл в режиме добавления
        with open(FILE_PATH, "a") as file:
            file.write(json.dumps(log_entry) + "\n")
            # # Сериализуем данные в строку JSON и записываем в файл
            # json.dump(log_entry, file)
            # # Добавляем перенос строки для разделения записей
            # file.write("\n")

        # Логируем успешное выполнение
        logging.info(f"Weather data fetched and saved: {log_entry}")
        print(f"[{datetime.now()}] Weather data fetched and saved successfully.")

    except requests.exceptions.RequestException as e:
        # Логируем ошибки HTTP-запроса
        logging.error(f"Error fetching weather data: {e}")
      #  print(f"[{datetime.now()}] Error fetching weather data: {e}")

# Планируем выполнение задачи раз в10ctr
schedule.every(10).seconds.do(fetch_weather)

if __name__ == "__main__":
    # Запускаем цикл планировщика
    logging.info("Starting the weather logger...")
    print("Starting the weather logger...")
    while True:
        # Выполняем запланированные задачи
        schedule.run_pending()
        # Задержка между проверками (1 секунда)
        time.sleep(1)
