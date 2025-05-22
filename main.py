from flask import Flask
import threading
import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from shutil import which

URL = "https://doithe365.com/doithecao"
CHECK_INTERVAL = 300

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
            print("Đã gửi tin nhắn Telegram!")
        else:
            print("Gửi Telegram thất bại:", response.text)
    except Exception as e:
        print("Lỗi gửi Telegram:", e)

def check_discount():
    print("=== Kiểm tra chiết khấu ===")
    chrome_path = which("chromium")
    driver_path = which("chromedriver")
    if not chrome_path or not driver_path:
        raise EnvironmentError("Không tìm thấy chromium trong môi trường!")

    options = Options()
    options.binary_location = chrome_path
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(URL)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "VINAPHONE-tab"))).click()
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "VINAPHONE")))

        table = driver.find_element(By.XPATH, '//div[@id="VINAPHONE"]//table')
        headers = table.find_elements(By.TAG_NAME, "th")
        rows = table.find_elements(By.TAG_NAME, "tr")

        index_500k = -1
        for i, header in enumerate(headers):
            if "500" in header.text:
                index_500k = i
                break

        if index_500k == -1:
            print("Không tìm thấy cột 500K")
            return

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if not cells:
                continue
            if "Thành viên" in cells[0].text:
                rate_text = cells[index_500k].text.strip().replace("%", "").replace(",", ".")
                rate = float(rate_text)
                print(f"Chiết khấu 500K (Thành viên): {rate}%")
                if rate <= 12.0:
                    send_telegram(rate)
                else:
                    print("Chưa đạt điều kiện gửi Telegram.")
                break

    except Exception as e:
        print("Lỗi xử lý:", e)
    finally:
        driver.quit()

def run_loop():
    while True:
        check_discount()
        time.sleep(CHECK_INTERVAL)

@app.route("/")
def home():
    return "Vinaphone monitor is running!"

threading.Thread(target=run_loop).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
