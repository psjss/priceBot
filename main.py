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

def get_pepe_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=pepe&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        print("🧠 CoinGecko Response:", data)
        if "pepe" not in data or "usd" not in data["pepe"]:
            raise ValueError("Missing PEPE price in response")
        return float(data["pepe"]["usd"])
    except Exception as e:
        return f"Error: {e}"

def send_regular_update():
    while True:
        price = get_pepe_price()
        if isinstance(price, float):
            message = f"📈 PEPE Price Update:\n\n💰 ${price:.8f} USD (Binance)"
        else:
            message = f"⚠️ Error fetching PEPE price:\n{price}"
        bot.send_message(chat_id=chat_id, text=message)
        time.sleep(1800)

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
