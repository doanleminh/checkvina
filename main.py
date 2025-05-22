
import requests
from bs4 import BeautifulSoup
import time
import threading
from flask import Flask
import os
from datetime import datetime, timedelta, timezone
import traceback

URL = "https://doithe365.com/doithecao"
app = Flask(__name__)

TELEGRAM_CHAT_ID = "5768955670"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHECK_INTERVAL = 30  # giây

def send_telegram(rate):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Thiếu TELEGRAM_TOKEN hoặc TELEGRAM_CHAT_ID")
        return

    message = f"Chiết khấu Vinaphone 500K hiện tại là {rate}%\n{URL}"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Đã gửi tin nhắn Telegram.")
        else:
            print("Gửi Telegram thất bại:", response.text)
    except Exception as e:
        print("Lỗi gửi Telegram:", e)

def check_discount():
    try:
        now = datetime.now(timezone(timedelta(hours=7)))
        print(now.strftime("[%Y-%m-%d %H:%M:%S UTC+7]"), "Đang kiểm tra chiết khấu...")

        res = requests.get(URL)
        soup = BeautifulSoup(res.text, "html.parser")

        tab = soup.find("div", id="VINAPHONE")
        if not tab:
            print("Không tìm thấy tab VINAPHONE.")
            return

        table = tab.find("table")
        headers = table.find_all("th")
        index_500k = -1
        for i, th in enumerate(headers):
            if "500" in th.text:
                index_500k = i
                break

        if index_500k == -1:
            print("Không tìm thấy cột 500K.")
            return

        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if cols and "Thành viên" in cols[0].text:
                rate = float(cols[index_500k].text.strip().replace("%", "").replace(",", "."))
                print(f"[{now.strftime('%H:%M:%S')}] Chiết khấu 500K (Thành viên): {rate}%")
                if rate <= 9.0:
                    send_telegram(rate)
                    print(">>> Đã gửi thông báo Telegram.")
                else:
                    print(">>> Không đạt điều kiện gửi Telegram.")
                break

        print("Hoàn tất kiểm tra.\n")

    except Exception as e:
        print("Lỗi khi kiểm tra chiết khấu:", e)
        traceback.print_exc()

def run_loop():
    while True:
        check_discount()
        print(f"==> Lặp lại lúc {datetime.now(timezone(timedelta(hours=7))).strftime('%H:%M:%S')} (UTC+7)")
        time.sleep(CHECK_INTERVAL)

@app.route("/")
def home():
    return "Vinaphone monitor is running!"

# Dùng daemon=True để đảm bảo thread không bị kill khi chạy nền trên Render
threading.Thread(target=run_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
