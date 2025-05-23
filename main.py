
from flask import Flask
from bs4 import BeautifulSoup
import requests
import threading
import time
import datetime
import os
import psutil

# Telegram token & chat_id
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or "5768955670"

URL = "https://doithe365.com/"
app = Flask(__name__)

def send_telegram(rate):
    if not TELEGRAM_TOKEN:
        print("Thiếu TELEGRAM_TOKEN", flush=True)
        return
    try:
        message = f"Chiết khấu Vinaphone 500K hiện tại là {rate}%."
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
        }
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Lỗi khi gửi Telegram: {e}", flush=True)

def check_discount():
    print(f"Đang kiểm tra chiết khấu...", flush=True)
    try:
        res = requests.get(URL, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        tab = soup.find("div", id="VINAPHONE")
        if not tab:
            print("Không tìm thấy tab VINAPHONE.", flush=True)
            return

        table = tab.find("table")
        headers = table.find_all("th")
        index_500k = -1
        for i, th in enumerate(headers):
            if "500" in th.text:
                index_500k = i
                break

        if index_500k == -1:
            print("Không tìm thấy cột 500K.", flush=True)
            return

        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if cols and "Thành viên" in cols[0].text:
                rate_text = cols[index_500k].text.strip().replace("%", "").replace(",", ".")
                rate = float(rate_text)
                print(f"Chiết khấu 500K (Thành viên): {rate}%", flush=True)
                if rate <= 9.0:
                    send_telegram(rate)
                else:
                    print("Không đạt điều kiện gửi Telegram.", flush=True)
                break
    except Exception as e:
        print(f"Lỗi khi xử lý: {e}", flush=True)
    finally:
        mem = psutil.Process(os.getpid()).memory_info().rss / 1024**2
        print(f"Memory usage: {mem:.2f} MB", flush=True)
        print("Hoàn tất kiểm tra\n", flush=True)
        del res, soup  # giải phóng bộ nhớ

def run_loop():
    while True:
        check_discount()
        time.sleep(30)

@app.route("/")
def index():
    return "Vinaphone monitor is running!"

if __name__ == "__main__":
    thread = threading.Thread(target=run_loop, daemon=True)
    thread.start()
    app.run(host="0.0.0.0", port=8080)
