import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import base64

# .envファイルを読み込む
load_dotenv()

# 環境変数からAPIキーを取得
ASTRONOMY_APPLICATION_ID = os.getenv("ASTRONOMY_APPLICATION_ID")
ASTRONOMY_APPLICATION_SEACRET = os.getenv("ASTRONOMY_APPLICATION_SEACRET")

# AstronomyAPIを利用して月のフェーズを取得
def get_moon_data(lat, lon):
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://api.astronomyapi.com/api/v2/bodies/positions?latitude={lat}&longitude={lon}&elevation=0&from_date={today}&to_date={today}&time=00:00:00"
    userpass = f"{ASTRONOMY_APPLICATION_ID}:{ASTRONOMY_APPLICATION_SEACRET}"
    authString = base64.b64encode(userpass.encode()).decode()
    headers = {
        "Authorization": f"Basic {authString}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch moon data: {response.status_code}")
        print(f"Response content: {response.content.decode('utf-8')}")
        return None