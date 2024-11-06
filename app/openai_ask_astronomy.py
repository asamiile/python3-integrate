import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import base64
from fetch_astronomy import get_moon_data, get_visible_constellations  # fetch_astronomy.pyから関数をインポート
from fetch_open_weather import get_weather_data  # fetch_open_weather.pyから関数をインポート

# .envファイルを読み込む
load_dotenv()

# 環境変数からAPIキーを取得
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_WEBHOOK_URL_ART = os.getenv("DISCORD_WEBHOOK_URL_ART")

# OpenAI APIキーを設定
client = OpenAI(api_key=OPENAI_API_KEY)

# 指定された緯度と経度
LATITUDE = os.getenv("LATITUDE")
LONGTITUDE = os.getenv("LONGTITUDE")

# 天気や天体情報を含むシステムメッセージを設定
system_message = """
You are a knowledgeable assistant in astronomy and weather forecasting. You have access to the latest weather data and astronomical information.
"""

# OpenAI APIを利用して質問を送信し、回答を取得
def ask_openai(question):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": question}
            ],
            max_tokens=600,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        return f"Error: {e}"

# Discordに通知を送信
def send_discord_notification(message):
    if DISCORD_WEBHOOK_URL_ART:
        data = {"content": message}
        response = requests.post(DISCORD_WEBHOOK_URL_ART, json=data)
        if response.status_code != 204:
            print(f"Failed to send notification: {response.status_code}")
            print(f"Response content: {response.content.decode('utf-8')}")
    else:
        print("Discord Webhook URL is not set.")

# メッセージを分割して送信
def send_long_message(message):
    max_length = 2000
    for i in range(0, len(message), max_length):
        send_discord_notification(message[i:i + max_length])

if __name__ == "__main__":
    # 天気情報を取得
    weather_data = get_weather_data(LATITUDE, LONGTITUDE)
    # 月のデータを取得
    moon_data = get_moon_data(LATITUDE, LONGTITUDE)
    # 観測できる星座の情報を取得
    constellations = get_visible_constellations(LATITUDE, LONGTITUDE)

    # 天気情報、月のデータ、星座のデータが取得できた場合
    if weather_data and moon_data and constellations:
        weather_description = weather_data['weather'][0]['description']
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']
        cloudiness = weather_data['clouds']['all']

        moon_phase = moon_data['data']['table']['rows'][1]['cells'][0]['extraInfo']['phase']['string']
        moonlight = "有り" if moon_phase not in ["New Moon", "Waning Crescent"] else "無し"

        # 観測できる星座のリストを作成
        constellations_list = ", ".join(constellations)

        # 質問を設定
        question = f"""
        本日、緯度: {LATITUDE}, 経度: {LONGTITUDE}の地点で夜空を撮影するのに適しているか知りたいです。以下の点について教えてください:
        1. 天気情報:
            - 天気: {weather_description}
            - 気温: {temperature}°C
            - 湿度: {humidity}%
            - 風速: {wind_speed} m/s
            - 雲量: {cloudiness}%
        2. 天体情報:
            - 月のフェーズ: {moon_phase}
            - 月明かりの有無: {moonlight}
            - 観測できる星座: {constellations_list}
        3. 夜空撮影に適しているかどうかの総合評価
        """

        # OpenAI APIを利用して質問を送信し、回答を取得
        answer = ask_openai(question)
        message = f"本日の天体情報:\n{answer}"
        print(message)
        # メッセージを分割して送信
        send_long_message(message)
    else:
        # 天気情報、月のデータ、星座のデータを取得できなかった場合のエラーメッセージ
        print("天気情報、月のデータ、または星座のデータを取得できませんでした。")