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

app = Flask(__name__)
URL = "https://doithe365.com/doithecao"

def send_telegram(rate):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = "5768955670"
    if not token or not chat_id:
        print("Thieu TELEGRAM_TOKEN hoac TELEGRAM_CHAT_ID")
        return
    message = "Chiet khau Vinaphone 500K hien tai la {}%\nhttps://doithe365.com/doithecao".format(rate)
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Da gui tin nhan Telegram!")
        else:
            print("Gui Telegram that bai:", response.text)
    except Exception as e:
        print("Loi gui Telegram:", e)

def check_discount():
    print("=== Kiem tra chiet khau ===")
    chrome_path = which("chromium")
    if not chrome_path:
        raise EnvironmentError("Khong tim thay chromium trong moi truong!")

    driver_path = which("chromedriver")
    if not driver_path:
        raise EnvironmentError("Khong tim thay chromedriver trong moi truong!")

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
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "VINAPHONE-tab"))).click()
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "VINAPHONE")))
        table = driver.find_element(By.XPATH, '//div[@id="VINAPHONE"]//table')
        headers = table.find_elements(By.TAG_NAME, "th")
        print("Header Titles:")
        for i, header in enumerate(headers):
            print(" - Cot {}: {}".format(i, header.text))

        index_500k = -1
        for i, header in enumerate(headers):
            if "500" in header.text:
                index_500k = i
                break

        if index_500k == -1:
            print("Khong tim thay cot 500K")
            return

        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if not cells:
                continue
            if "Thanh vien" in cells[0].text:
                rate_text = cells[index_500k].text.strip().replace("%", "").replace(",", ".")
                rate = float(rate_text)
                print("Chiet khau 500K (Thanh vien): {}%".format(rate))
                if rate <= 12.0:
                    send_telegram(rate)
                else:
                    print("Chua dat dieu kien gui Telegram.")
                break
    except Exception as e:
        print("Loi xu ly:", e)
    finally:
        driver.quit()

def run_loop():
    while True:
        check_discount()
        time.sleep(300)

@app.route("/")
def home():
    return "Vinaphone monitor dang chay!"

threading.Thread(target=run_loop).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
