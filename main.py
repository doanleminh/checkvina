from flask import Flask
import threading
import time
import os
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5768955670")

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        r = requests.post(url, data=data)
        print("Sent!" if r.ok else f"Failed: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

def check_discount():
    print("Checking discount...")
    # Thay thế bằng logic thực tế
    rate = 11.5
    send_telegram(f"Chiết khấu Vinaphone 500K hiện tại là {rate}%")

def run_loop():
    while True:
        check_discount()
        time.sleep(300)

@app.route("/")
def home():
    return "Vinaphone monitor is running!"

threading.Thread(target=run_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)