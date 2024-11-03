import os
import requests
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# 環境変数からAPIキーを取得
API_KEY = os.getenv("CINII_API_KEY")
DISCORD_WEBHOOK_URL_SCHOLAR = os.getenv("DISCORD_WEBHOOK_URL_SCHOLAR")
KEYWORDS = ['美学', '哲学', '詩学', '環境', '伝統行事', '博多どんたく', '伝統空間', 'コミュニティ', '人と文化', 'オンラインゲーム', 'ギルド']

def fetch_cinii_data(api_key, keywords):
    results = []
    base_url = "https://ci.nii.ac.jp/opensearch/search"

    for keyword in keywords:
        params = {
            'appid': api_key,
            'format': 'json',
            'q': keyword,
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            results.append({
                'keyword': keyword,
                'data': response.json()
            })
        else:
            print(f"Error fetching data for keyword '{keyword}': {response.status_code}")
            response.raise_for_status()

    return results

def send_discord_notification(message):
    if DISCORD_WEBHOOK_URL_SCHOLAR:
        data = {"content": message}
        response = requests.post(DISCORD_WEBHOOK_URL_SCHOLAR, json=data)
        if response.status_code != 204:
            print(f"Failed to send notification: {response.status_code}")
            print(f"Response content: {response.content.decode('utf-8')}")
    else:
        print("Discord Webhook URL is not set.")

def send_long_message(message):
    max_length = 2000
    for i in range(0, len(message), max_length):
        send_discord_notification(message[i:i + max_length])

# Ciniiは出版年月日が年のみ、月のみの場合があるので、
# 最新n件を取得する
if __name__ == "__main__":
    if not API_KEY:
        print("Error: CINII_API_KEY is not set in the .env file.")
        exit(1)

    try:
        results = fetch_cinii_data(API_KEY, KEYWORDS)
        for result in results:
            print(f"CiNii Search Results: {result['keyword']}")
            messages = []
            for i in range(min(3, len(result['data']['items']))):
                item = result['data']['items'][i]
                print(f"Title: {item['title']}")
                print(f"Link: {item['link']['@id']}")
                print(f"Publication Date: {item['prism:publicationDate']}")
                print(f"Publisher: {item['dc:publisher']}")
                print()  # 空行を挿入して見やすくする

                message = (
                    f"**Title:** {item['title']}\n"
                    f"**Link:** {item['link']['@id']}\n"
                    f"**Publication Date:** {item['prism:publicationDate']}\n"
                    f"**Publisher:** {item['dc:publisher']}\n"
                )
                messages.append(message)

            if messages:
                full_message = f"CiNii Search Results for {result['keyword']}:\n\n" + "\n\n".join(messages)
                send_long_message(full_message)

        # 成功通知を送信
        # send_discord_notification("fetch_cinii.py ran successfully.")

    except Exception as e:
        print(f"Error: {e}")
        # 失敗通知を送信
        # send_discord_notification(f"fetch_cinii.py failed with error: {e}")