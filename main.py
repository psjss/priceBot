import requests
import time
import threading
import os
from flask import Flask
from telegram import Bot

bot_token = os.getenv("BOT_TOKEN")
chat_id = int(os.getenv("CHAT_ID"))
bot = Bot(token=bot_token)

app = Flask(__name__)

@app.route('/')
def home():
    return "PEPE bot is running ✅"

latest_price = None  # Global variable

def get_pepe_price():
    global latest_price
    url = "https://api.binance.com/api/v3/ticker/price?symbol=PEPEUSDT"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        if "price" not in data:
            raise ValueError("Missing 'price' in response")
        latest_price = float(data["price"])
        return latest_price
    except Exception as e:
        print(f"⚠️ Fetch error: {e}")
        return latest_price if latest_price else f"Error: {e}"

def send_regular_update():
    while True:
        price = get_pepe_price()
        if isinstance(price, float):
            message = f"📈 PEPE Price Update:\n\n💰 ${price:.8f} USD (Binance)"
        else:
            message = f"⚠️ Error fetching PEPE price:\n{price}"
        bot.send_message(chat_id=chat_id, text=message)
        time.sleep(600)

def monitor_volatility():
    last_price = get_pepe_price()
    while True:
        time.sleep(300)
        current_price = get_pepe_price()
        if isinstance(last_price, float) and isinstance(current_price, float):
            change = ((current_price - last_price) / last_price) * 100
            if abs(change) >= 2:
                direction = "📈 Up" if change > 0 else "📉 Down"
                alert = (
                    f"🚨 PEPE Sudden Move Alert ({direction})\n\n"
                    f"Old: ${last_price:.8f}\n"
                    f"Now: ${current_price:.8f}\n"
                    f"Change: {change:.2f}% in 5 mins!"
                )
                bot.send_message(chat_id=chat_id, text=alert)
        last_price = current_price

if __name__ == "__main__":
    threading.Thread(target=send_regular_update).start()
    threading.Thread(target=monitor_volatility).start()
    app.run(host="0.0.0.0", port=8080)
