import os, logging, io, yfinance as yf, matplotlib.pyplot as plt
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# الإعدادات الأساسية
TOKEN = os.getenv('TELEGRAM_TOKEN')
URL = f"https://{os.getenv('RAILWAY_STATIC_URL')}"
PORT = int(os.getenv('PORT', 8080))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# دالة اللوحة الاحترافية
def get_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("👤 حسابي", callback_data="acc"), InlineKeyboardButton("🌐 English", callback_data="lang"))
    kb.add(InlineKeyboardButton("📡 إضافة قناة", callback_data="add_ch"), InlineKeyboardButton("📡 قنواتي", callback_data="my_ch"))
    kb.add(InlineKeyboardButton("🛡️ ويب هوك", callback_data="webk"), InlineKeyboardButton("🔐 رمز أمان", callback_data="token"))
    kb.add(InlineKeyboardButton("📈 مؤشر الأسهم", callback_data="index"), InlineKeyboardButton("💰 سعر سهم", callback_data="price"))
    kb.add(InlineKeyboardButton("🚀 التداول الآلي", callback_data="auto"), InlineKeyboardButton("📧 الدعم", callback_data="supp"))
    return kb

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("📈 **Mr.MOH Bot v2.0**\nجاهز للعمل بأقصى سرعة.", reply_markup=get_keyboard(), parse_mode="Markdown")

@dp.callback_query_handler(lambda c: True)
async def buttons(c: types.CallbackQuery):
    await bot.answer_callback_query(c.id) # حل مشكلة التعليق
    if c.data == "price":
        await bot.send_message(c.from_user.id, "أرسل رمز السهم الآن (مثل: NVDA)")
    else:
        await bot.send_message(c.from_user.id, "✅ تم استلام طلبك.")

@dp.message_handler()
async def stock(message: types.Message):
    sym = message.text.upper()
    try:
        t = yf.Ticker(sym)
        price = t.fast_info['last_price']
        await message.answer(f"📊 **{sym}**\nالسعر الحالي: `${price:.2f}`", parse_mode="Markdown")
    except:
        await message.answer("❌ الرمز غير صحيح.")

# تشغيل الويب هوك
if __name__ == '__main__':
    start_webhook(dp, f'/webhook/{TOKEN}', on_startup=lambda d: bot.set_webhook(f"{URL}/webhook/{TOKEN}"), host='0.0.0.0', port=PORT)
