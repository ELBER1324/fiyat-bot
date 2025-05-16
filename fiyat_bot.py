
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
from telegram import Bot
import time, os

# 📲 Telegram Ayarları (GitHub Secrets ile çalışacak şekilde env'den okuyoruz)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# 🛒 İzlenecek Ürünler (Buraya kendi linklerini ekleyebilirsin)
products = [
    {
        'name': 'Trendyol Örnek Ürün',
        'url': 'https://www.trendyol.com/ürün-linki',
        'site': 'trendyol'
    },
    {
        'name': 'Hepsiburada Örnek Ürün',
        'url': 'https://www.hepsiburada.com/ürün-linki',
        'site': 'hepsiburada'
    }
]

# 📤 Telegram Bildirim Fonksiyonu
def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=message)

# 🔍 Fiyat Çekme Fonksiyonu
def get_price(driver, url, site):
    driver.get(url)
    time.sleep(3)

    if site == 'trendyol':
        price_element = driver.find_element(By.CLASS_NAME, 'prc-dsc')
    elif site == 'hepsiburada':
        price_element = driver.find_element(By.CLASS_NAME, 'priceValue')
    else:
        return None

    price_text = price_element.text.replace('TL', '').replace('.', '').replace(',', '.').strip()
    return float(price_text)

# 📦 Fiyat Kaydetme & Karşılaştırma Fonksiyonu
def update_price_history(product_name, current_price):
    CSV_FILE = 'fiyat_takip.csv'
