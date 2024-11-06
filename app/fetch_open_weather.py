import os
import requests
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# 環境変数からAPIキーを取得
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# OpenWeather APIを利用して天気情報を取得
def get_weather_data(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch weather data: {response.status_code}")
        print(f"Response content: {response.content.decode('utf-8')}")
        return None