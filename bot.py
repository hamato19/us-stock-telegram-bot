import os
import alpaca_trade_api as tradeapi
from aiogram import Bot, Dispatcher, executor, types

# استدعاء المتغيرات من إعدادات Render
API_TOKEN = os.getenv('TELEGRAM_TOKEN')
ALPACA_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET = os.getenv('ALPACA_SECRET_KEY')
BASE_URL = 'https://paper-api.alpaca.markets' # رابط التداول الورقي

# الربط مع Alpaca
api = tradeapi.REST(ALPACA_KEY, ALPACA_SECRET, BASE_URL, api_version='v2')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("💹 **تم تفعيل Mr.MOH الأسهم الأمريكية!**\n\nأرسل رمز السهم (مثل AAPL) لجلب السعر المباشر من محفظتك الورقية.")

@dp.message_handler()
async def get_stock(message: types.Message):
    symbol = message.text.upper()
    try:
        # جلب آخر سعر من Alpaca
        trade = alpaca.get_latest_trade(symbol)
        price = trade.price
        
        await message.reply(f"📊 **سهم {symbol}**\n💰 السعر الحالي: `${price}`\n✅ المصدر: Alpaca Markets")
    except Exception as e:
        await message.reply(f"⚠️ خطأ: تأكد من رمز السهم أو إعدادات الـ API.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
