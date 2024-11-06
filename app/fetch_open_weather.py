import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# .envファイルを読み込む
load_dotenv()

# 環境変数からAPIキーを取得
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# 指定された緯度と経度
LATITUDE = os.getenv("LATITUDE")
LONGTITUDE = os.getenv("LONGTITUDE")

# OpenWeather APIを利用して天気情報を取得
def get_weather_data(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch weather data: {response.status_code}")
        print(f"Response content: {response.content.decode('utf-8')}")
        return None

# 月のフェーズを取得する関数（簡易版）
def get_moon_phase():
    now = datetime.now()
    new_moon = datetime(2023, 11, 13)  # 新月の日付を設定
    days_since_new_moon = (now - new_moon).days % 29.53
    if days_since_new_moon < 1 or days_since_new_moon > 28.53:
        return "New Moon"
    elif days_since_new_moon < 7.38:
        return "First Quarter"
    elif days_since_new_moon < 14.77:
        return "Full Moon"
    elif days_since_new_moon < 22.15:
        return "Last Quarter"
    else:
        return "Waning Crescent"

weather_data = get_weather_data(LATITUDE, LONGTITUDE, OPENWEATHER_API_KEY)
moon_phase = get_moon_phase()

if weather_data:
    weather_description = weather_data['weather'][0]['description']
    temperature = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']
    cloudiness = weather_data['clouds']['all']

    print(f"Weather Description: {weather_description}")
    print(f"Temperature: {temperature}°C")
    print(f"Humidity: {humidity}%")
    print(f"Wind Speed: {wind_speed} m/s")
    print(f"Cloudiness: {cloudiness}%")
    print(f"Moon Phase: {moon_phase}")

else:
    print("Failed to retrieve weather data.")