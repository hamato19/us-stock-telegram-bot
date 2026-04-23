import os
import logging
import asyncio
import io
import yfinance as yf
import matplotlib.pyplot as plt
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- الإعدادات (تأكد من ضبطها في Railway Variables) ---
API_TOKEN = os.getenv('TELEGRAM_TOKEN')
WEBHOOK_HOST = f"https://{os.getenv('RAILWAY_STATIC_URL')}"
WEBHOOK_PATH = f'/webhook/{API_TOKEN}'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
PORT = int(os.getenv('PORT', 8080))

# تهيئة البوت
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- الدوال المساعدة ---

async def generate_stock_chart(symbol):
    """توليد رسم بياني احترافي للسهم"""
    try:
        data = yf.download(symbol, period="5d", interval="1h", progress=False)
        if data.empty: return None
        
        plt.figure(figsize=(10, 6))
        plt.style.use('dark_background')
        plt.plot(data.index, data['Close'], color='#00ffcc', linewidth=2)
        plt.fill_between(data.index, data['Close'], color='#00ffcc', alpha=0.1)
        plt.title(f"{symbol} - Last 5 Days Performance", color='white', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.2)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        return buf
    except:
        return None

def get_main_menu():
    """إنشاء اللوحة بنفس تصميم الصورة المطلوبة بالضبط"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("👤 حسابي", callback_data="acc"),
        InlineKeyboardButton("🌐 English", callback_data="lang")
    )
    keyboard.add(
        InlineKeyboardButton("📡 إضافة قناة", callback_data="add_ch"),
        InlineKeyboardButton("📡 قنواتي", callback_data="my_ch")
    )
    keyboard.add(
        InlineKeyboardButton("🛡️ ويب هوك", callback_data="webk"),
        InlineKeyboardButton("🔐 رمز أمان", callback_data="token")
    )
    keyboard.add(
        InlineKeyboardButton("📈 مؤشر الأسهم", callback_data="market_index"),
        InlineKeyboardButton("💰 سعر سهم", callback_data="get_price")
    )
    keyboard.add(
        InlineKeyboardButton("🚀 التداول الآلي", callback_data="auto"),
        InlineKeyboardButton("📧 الدعم", callback_data="supp")
    )
    return keyboard

# --- معالجة الأوامر ---

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    welcome_text = (
        "📈 **Mr.MOH Bot**\n"
        "مرحباً بك في منصة التحليل المتطورة.\n\n"
        "استخدم الأزرار أدناه للتحكم في حسابك أو أرسل رمز السهم مباشرة (مثال: AAPL)."
    )
    await message.reply(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

@dp.callback_query_handler(lambda c: True)
async def handle_all_callbacks(callback_query: types.CallbackQuery):
    """معالج الأزرار السريع"""
    # استجابة فورية لتليجرام لإزالة علامة الانتظار
    await bot.answer_callback_query(callback_query.id)
    
    user_id = callback_query.from_user.id
    data = callback_query.data

    if data == "acc":
        await bot.send_message(user_id, "👤 **بيانات حسابك:**\nالحالة: نشط ✅\nالخطة: بريميوم")
    elif data == "market_index":
        await bot.send_message(user_id, "📈 **أداء المؤشرات الرئيسية:**\nS&P 500: 🟢\nNasdaq: 🟢\nDow Jones: 🔴")
    elif data == "get_price":
        await bot.send_message(user_id, "⌨️ يرجى كتابة رمز السهم مباشرة في الشات (مثال: TSLA)")
    elif data == "webk":
        await bot.send_message(user_id, f"🛡️ **رابط الويب هوك الخاص بك:**\n`{WEBHOOK_HOST}/hook/{user_id}`")
    else:
        await bot.send_message(user_id, "🚧 هذه الميزة قيد التطوير حالياً.")

@dp.message_handler()
async def handle_stock_request(message: types.Message):
    """جلب سعر السهم والشارت تلقائياً عند كتابة الرمز"""
    symbol = message.text.upper()
    status_msg = await message.answer(f"🔍 جاري تحليل {symbol}...")
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        current_price = info['last_price']
        
        chart_img = await generate_stock_chart(symbol)
        
        caption = (
            f"📊 **تقرير سهم: {symbol}**\n"
            f"━━━━━━━━━━━━━━\n"
            f"💰 السعر الحالي: `${current_price:.2f}`\n"
            f"📈 التغيير: {'🟢' if info['year_change'] > 0 else '🔴'} {info['year_change']:.2f}%\n"
            f"━━━━━━━━━━━━━━"
        )
        
        if chart_img:
            await bot.send_photo(message.chat.id, chart_img, caption=caption, parse_mode="Markdown")
        else:
            await message.answer(caption, parse_mode="Markdown")
            
    except Exception:
        await message.answer(f"❌ تعذر العثور على بيانات للسهم: {symbol}")
    
    await status_msg.delete()

# --- إعدادات التشغيل ---

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host='0.0.0.0',
        port=PORT,
    )
