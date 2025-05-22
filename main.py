
from flask import Flask
import threading
import time
import os
import requests

app = Flask(__name__)

TELEGRAM_CHAT_ID = "5768955670"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Thiếu TELEGRAM_TOKEN hoặc TELEGRAM_CHAT_ID")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        res = requests.post(url, data=data)
        print("Đã gửi Telegram!" if res.status_code == 200 else f"Lỗi: {res.text}")
    except Exception as e:
        print("Lỗi gửi Telegram:", e)

def check_discount():
    print("Giả lập kiểm tra chiết khấu")
    send_telegram("Chiết khấu Vinaphone 500K hiện tại là 11.5%")

def run_loop():
    while True:
        check_discount()
        time.sleep(300)

@app.route("/")
def home():
    return "Vinaphone monitor is running!"

if __name__ == "__main__":
    threading.Thread(target=run_loop).start()
    app.run(host="0.0.0.0", port=8080)
