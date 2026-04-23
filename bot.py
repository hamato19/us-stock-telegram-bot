from fastapi import FastAPI, Request
import alpaca_trade_api as tradeapi
import asyncio
from aiogram import Bot

app = FastAPI()

# إعداداتك (يفضل وضعها في Secrets)
ALPACA_KEY = 'YOUR_KEY'
ALPACA_SECRET = 'YOUR_SECRET'
TELEGRAM_TOKEN = 'YOUR_TOKEN'
CHAT_ID = 'YOUR_CHAT_ID'

bot = Bot(token=TELEGRAM_TOKEN)
api = tradeapi.REST(ALPACA_KEY, ALPACA_SECRET, 'https://paper-api.alpaca.markets')

# هذا هو رابط الـ Webhook الذي ستضعه في TradingView
@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    
    # مثال: إذا وصلت إشارة شراء من TradingView
    symbol = data.get('ticker')
    action = data.get('action') # buy or sell
    
    if action == 'buy':
        # تنفيذ أمر شراء في Alpaca
        api.submit_order(symbol=symbol, qty=1, side='buy', type='market', time_in_force='gtc')
        # إرسال تنبيه لك على التليجرام
        await bot.send_message(CHAT_ID, f"🚀 تم تنفيذ أمر شراء لسهم {symbol} آلياً!")
    
    return {"status": "success"}
