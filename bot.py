import os
import logging
import uuid
import io
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import alpaca_trade_api as tradeapi

# --- الإعدادات والمفاتيح ---
TOKEN = os.getenv('TELEGRAM_TOKEN')
ALPACA_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET = os.getenv('ALPACA_SECRET_KEY')

# إعدادات الويب هوك لـ Railway
WEBHOOK_HOST = f"https://{os.getenv('RAILWAY_STATIC_URL')}"
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT', 8080))

# --- تهيئة البوت وقاعدة البيانات المؤقتة ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
alpaca = tradeapi.REST(ALPACA_KEY, ALPACA_SECRET, base_url='https://paper-api.alpaca.markets')

users_db = {}

def get_user_data(user_id):
    if user_id not in users_db:
        users_db[user_id] = {
            'lang': 'ar',
            'channel': None,
            'token': str(uuid.uuid4())[:8],
            'alerts_count': 0
        }
    return users_db[user_id]

# --- وظائف الرسوم البيانية ---
def generate_chart(symbol):
    try:
        # جلب بيانات تاريخية لآخر 5 أيام
        bars = alpaca.get_bars(symbol, '1Hour', limit=100).df
        if bars.empty: return None

        plt.figure(figsize=(10, 5))
        plt.style.use('dark_background')
        plt.plot(bars.index, bars['close'], color='#00ffcc', linewidth=2)
        plt.fill_between(bars.index, bars['close'], color='#00ffcc', alpha=0.1)
        plt.title(f"Chart: {symbol}", color='white', fontsize=15)
        plt.grid(axis='y', linestyle='--', alpha=0.3)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        return buf
    except:
        return None

# --- الأزرار والقوائم ---
async def get_main_keyboard(user_id):
    data = get_user_data(user_id)
    lang = data['lang']
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    if lang == 'ar':
        keyboard.add(InlineKeyboardButton("👤 حسابي", callback_data="acc"), InlineKeyboardButton("🌐 English", callback_data="lang"))
        keyboard.add(InlineKeyboardButton("📡 إضافة قناة", callback_data="add_ch"), InlineKeyboardButton("📡 قنواتي", callback_data="my_ch"))
        keyboard.add(InlineKeyboardButton("🛡️ ويب هوك", callback_data="webk"), InlineKeyboardButton("🔐 رمز أمان", callback_data="token"))
        keyboard.add(InlineKeyboardButton("🚀 التداول الآلي", callback_data="auto"), InlineKeyboardButton("📧 الدعم", callback_data="supp"))
    else:
        keyboard.add(InlineKeyboardButton("👤 My Account", callback_data="acc"), InlineKeyboardButton("🌐 العربية", callback_data="lang"))
        keyboard.add(InlineKeyboardButton("📡 Add Channel", callback_data="add_ch"), InlineKeyboardButton("📡 Channels", callback_data="my_ch"))
        keyboard.add(InlineKeyboardButton("🛡️ Webhook", callback_data="webk"), InlineKeyboardButton("🔐 Security", callback_data="token"))
        keyboard.add(InlineKeyboardButton("🚀 Auto Trade", callback_data="auto"), InlineKeyboardButton("📧 Support", callback_data="supp"))
    return keyboard

# --- معالجة الأوامر ---
@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    await message.reply("📈 **Mr.MOH Bot**\nمرحباً بك في منصة التحليل المتطورة.", reply_markup=await get_main_keyboard(message.from_user.id), parse_mode="Markdown")

@dp.callback_query_handler(lambda c: True)
async def handle_callbacks(c: types.CallbackQuery):
    u_id = c.from_user.id
    data = get_user_data(u_id)
    
    if c.data == "lang":
        data['lang'] = 'en' if data['lang'] == 'ar' else 'ar'
        await bot.edit_message_reply_markup(u_id, c.message.message_id, reply_markup=await get_main_keyboard(u_id))
    
    elif c.data == "acc":
        text = f"👤 **Profile**\n🆔 ID: `{u_id}`\n🔐 Token: `{data['token']}`\n📢 Channel: {'Connected' if data['channel'] else 'None'}"
        await bot.send_message(u_id, text, parse_mode="Markdown")
        
    elif c.data == "webk":
        if not data['channel']:
            await bot.send_message(u_id, "⚠️ يجب ربط قناة أولاً!")
        else:
            url = f"{WEBHOOK_HOST}/hook/{u_id}?key={data['token']}"
            await bot.send_message(u_id, f"🔗 **Webhook URL:**\n`{url}`", parse_mode="Markdown")
    
    await bot.answer_callback_query(c.id)

@dp.message_handler()
async def stock_request(message: types.Message):
    symbol = message.text.upper()
    wait_msg = await message.answer("🔍 جاري جلب البيانات وتحليل الشارت...")
    
    try:
        quote = alpaca.get_latest_quote(symbol)
        chart = generate_chart(symbol)
        
        caption = (
            f"📊 **تقرير سهم: {symbol}**\n"
            f"━━━━━━━━━━━━━━\n"
            f"💰 السعر الحالي: `${quote.bp}`\n"
            f"🟢 عرض: `${quote.ap}` | 🔴 طلب: `${quote.bp}`\n"
            f"⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}\n"
            f"━━━━━━━━━━━━━━"
        )
        
        if chart:
            await bot.send_photo(message.chat.id, chart, caption=caption, parse_mode="Markdown")
        else:
            await message.answer(caption, parse_mode="Markdown")
            
    except Exception as e:
        await message.answer(f"❌ لم يتم العثور على السهم: {symbol}")
    
    await wait_msg.delete()

# --- تشغيل الويب هوك ---
async def on_startup(dp): await bot.set_webhook(WEBHOOK_URL)
async def on_shutdown(dp): await bot.delete_webhook()

if __name__ == '__main__':
    start_webhook(dispatcher=dp, webhook_path=WEBHOOK_PATH, on_startup=on_startup, on_shutdown=on_shutdown, host=WEBAPP_HOST, port=WEBAPP_PORT)
