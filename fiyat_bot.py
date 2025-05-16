from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
from telegram import Bot
import time, os
import traceback  # HATA AYDINLATMA İÇİN

# 📲 TELEGRAM BİLGİLERİ
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# 🛒 ÜRÜNLER
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

# 📤 TELEGRAM MESAJ GÖNDERME
def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=message)

# 🔍 FİYAT ÇEKME
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

# 📊 CSV'YE KAYDET VE KARŞILAŞTIR
def update_price_history(product_name, current_price):
    CSV_FILE = 'fiyat_takip.csv'

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=['Product', 'Price', 'Time'])

    new_data = pd.DataFrame({
        'Product': [product_name],
        'Price': [current_price],
        'Time': [pd.Timestamp.now()]
    })

    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

    product_df = df[df['Product'] == product_name]
    if len(product_df) >= 2:
        last_two = product_df.tail(2)['Price'].values
        if last_two[1] < last_two[0]:
            send_telegram_message(f"🔻 {product_name} fiyat düştü!\nEski: {last_two[0]} TL ➔ Yeni: {last_two[1]} TL")
        else:
            print(f"Fiyat değişmedi: {product_name}")

# 🛠️ BOTU ÇALIŞTIR
def main():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)

    for product in products:
        try:
            print(f"{product['name']} fiyatı kontrol ediliyor...")
            current_price = get_price(driver, product['url'], product['site'])
            print(f"Şu anki fiyat: {current_price} TL")
            update_price_history(product['name'], current_price)
        except Exception as e:
            print(f"Hata: {e}")
            traceback.print_exc()

    driver.quit()

if __name__ == '__main__':
    main()
