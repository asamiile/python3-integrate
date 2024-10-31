import os
from openai import OpenAI
from dotenv import load_dotenv
import requests

# .envファイルを読み込む
load_dotenv()

# 環境変数からAPIキーを取得
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_WEBHOOK_URL_AIASSITANT = os.getenv("DISCORD_WEBHOOK_URL_AIASSITANT")

# OpenAI APIキーを設定
client = OpenAI(api_key=OPENAI_API_KEY)

# 指定された緯度と経度
LATITUDE = os.getenv("LATITUDE")
LONGTITUDE = os.getenv("LONGTITUDE")

# 天気や天体情報を含むシステムメッセージを設定
system_message = """
You are a knowledgeable assistant in astronomy and weather forecasting. You have access to the latest weather data and astronomical information.
"""

# 質問を設定
question = f"""
本日、緯度: {LATITUDE}, 経度: {LONGTITUDE}の地点で夜空を撮影するのに適しているか知りたいです。以下の点について教えてください:
1. 天気情報:
    - 対象地点の天気
    - 夜空の明るさ
    - 夜の雲量
2. 天体情報:
    - 月のフェーズ
    - 月明かりの有無
3. 夜空撮影に適した条件を満たしているかどうか
"""

def ask_openai(question):
    try:
        response = client.chat.completions.create(model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": question}
        ],
        max_tokens=500,
        temperature=0.3)
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        return f"Error: {e}"

def send_discord_notification(message):
    if DISCORD_WEBHOOK_URL_AIASSITANT:
        data = {"content": message}
        response = requests.post(DISCORD_WEBHOOK_URL_AIASSITANT, json=data)
        if response.status_code != 204:
            print(f"Failed to send notification: {response.status_code}")
    else:
        print("Discord Webhook URL is not set.")

if __name__ == "__main__":
    answer = ask_openai(question)
    print(f"本日の天体情報: {answer}")
    send_discord_notification(f"本日の天体情報: {answer}")