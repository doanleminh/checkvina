from flask import Flask
import threading
import time
import os
import requests
import datetime
from bs4 import BeautifulSoup

URL = "https://doithe365.com/doithecao"
app = Flask(__name__)


def send_telegram(rate):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = "5768955670"
    if not token or not chat_id:
        print("Thiếu TELEGRAM_TOKEN hoặc TELEGRAM_CHAT_ID")
        return

    message = f"Chiết khấu Vinaphone 500K hiện tại là {rate}%\nhttps://doithe365.com/doithecao"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}

    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Đã gửi Telegram.")
        else:
            print("Gửi Telegram thất bại:", response.text)
    except Exception as e:
        print("Lỗi gửi Telegram:", e)


def check_discount():
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC+7')}] Đang kiểm tra chiết khấu...")
    try:
        res = requests.get(URL, timeout=10)
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
                print(f"Chiết khấu 500K (Thành viên): {rate}%")
                if rate <= 9.0:
                    send_telegram(rate)
                else:
                    print("Không đạt điều kiện gửi Telegram.")
                break
        print("Hoàn tất kiểm tra.\n")
    except Exception as e:
        print("Lỗi khi kiểm tra chiết khấu:", e)


def run_loop():
    while True:
        check_discount()
        time.sleep(30)


@app.route("/")
def home():
    return "Vinaphone monitor is running!"


threading.Thread(target=run_loop).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
