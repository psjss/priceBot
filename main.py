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
    return "PEPE + BTC Bot is running ✅"

latest_pepe_price = None
latest_btc_price = None
pepe_price_history = []

# === Fetch price from Binance ===
def fetch_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        res = requests.get(url, timeout=10)
        return float(res.json()['price'])
    except Exception as e:
        print(f"Error fetching {symbol} price: {e}")
        return None

# === Regular 10-min updates for PEPE + BTC ===
def send_regular_update():
    global latest_pepe_price, latest_btc_price
    while True:
        pepe_price = fetch_price("PEPEUSDT")
        btc_price = fetch_price("BTCUSDT")

        if pepe_price and btc_price:
            latest_pepe_price = pepe_price
            latest_btc_price = btc_price

            message = (
                f"📊 10-Minute Price Update:\n"
                f"🐸 PEPE: ${pepe_price:.8f}\n"
                f"💠 BTC: ${btc_price:,.2f}"
            )
            bot.send_message(chat_id=chat_id, text=message)

        time.sleep(600)

# === 5-min PEPE volatility monitor ===
def monitor_volatility():
    global pepe_price_history
    while True:
        pepe_price = fetch_price("PEPEUSDT")
        if pepe_price:
            pepe_price_history.append(pepe_price)
            if len(pepe_price_history) > 5:
                pepe_price_history.pop(0)

            if len(pepe_price_history) == 5:
                old = pepe_price_history[0]
                change = ((pepe_price - old) / old) * 100
                if abs(change) >= 2:
                    direction = "📈 Up" if change > 0 else "📉 Down"
                    alert = (
                        f"🚨 PEPE Sudden Move Alert ({direction})\n\n"
                        f"Old: ${old:.8f}\n"
                        f"Now: ${pepe_price:.8f}\n"
                        f"Change: {change:.2f}% in 5 mins!"
                    )
                    bot.send_message(chat_id=chat_id, text=alert)

        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=send_regular_update).start()
    threading.Thread(target=monitor_volatility).start()
    app.run(host="0.0.0.0", port=8080)
