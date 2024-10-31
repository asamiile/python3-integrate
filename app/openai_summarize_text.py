import os
from openai import OpenAI
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# 環境変数からAPIキーを取得
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

def summarize_text(text):
    """与えられたテキストを要約する関数"""
    try:
        # OpenAIのChat APIを使用して要約を作成
        response = client.chat.completions.create(model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes texts."},
            {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
        ],
        max_tokens=100,
        temperature=0.5)

        # 要約を取得
        summary = response.choices[0].message.content.strip()
        return summary

    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return "Error occurred while summarizing text."

# 要約したいテキスト
text_to_summarize = "This is a test text to summarize."
# 要約を出力
print(summarize_text(text_to_summarize))