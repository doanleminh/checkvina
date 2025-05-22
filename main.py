from flask import Flask
import threading
import time
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = "5768955670"
URL = "https://doithe365.com/doithecao"

def send_telegram(rate):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID")
        return

    message = f"Chiet khau Vinaphone 500K hien tai la {rate}%\nhttps://doithe365.com/doithecao"
    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data={"chat_id": TELEGRAM_CHAT_ID, "text": message}
    )

    if response.status_code == 200:
        print("Telegram message sent successfully.")
    else:
        print("Failed to send Telegram message:", response.text)

def check_discount():
    try:
        res = requests.get(URL)
        soup = BeautifulSoup(res.text, "html.parser")

        tab = soup.find("div", id="VINAPHONE")
        if not tab:
            print("Cannot find VINAPHONE tab.")
            return

        table = tab.find("table")
        headers = table.find_all("th")
        index_500k = -1
        for i, th in enumerate(headers):
            if "500" in th.text:
                index_500k = i
                break

        if index_500k == -1:
            print("500K column not found.")
            return

        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if cols and "Thành viên" in cols[0].text:
                rate = float(cols[index_500k].text.strip().replace("%", "").replace(",", "."))
                print(f"Chiết khấu 500K (Thành viên): {rate}%")
                if rate <= 12.0:
                    send_telegram(rate)
                break
    except Exception as e:
        print("Error during scraping:", e)

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
