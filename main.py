import requests  # Для выполнения HTTP-запросов
import json      # Для работы с JSON-данными
from datetime import datetime  # Для добавления временных меток
import schedule  # Для создания расписания задач
import time      # Для функции задержки выполнения

# URL API сервиса погоды OpenWeather
API_URL = "https://api.openweathermap.org/data/2.5/weather"

# Ваш API-ключ для доступа к OpenWeather (замените на свой)
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


        # Открываем файл в режиме добавления (append)
        with open(FILE_PATH, "a") as file:
            # Сериализуем данные в строку JSON и записываем в файл
            json.dump(log_entry, file)
            # Добавляем перенос строки для разделения записей
            file.write("\n")

        # Уведомляем пользователя, что данные успешно сохранены
        print(f"[{datetime.now()}] Weather data fetched and saved successfully.")

    except requests.exceptions.RequestException as e:
        # Обрабатываем ошибки HTTP-запроса и выводим сообщение
        print(f"[{datetime.now()}] Error fetching weather data: {e}")

# Планируем выполнение задачи раз в минуту
schedule.every(10).seconds.do(fetch_weather)

if __name__ == "__main__":
    # Запускаем цикл планировщика
    print("Starting the weather logger...")
    while True:
        # Выполняем запланированные задачи
        schedule.run_pending()
        # Задержка между проверками (1 секунда)
        time.sleep(1)