import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# --- الإعدادات ---
API_TOKEN = 'ضع_هنا_توكن_البوت_الخاص_بك'
ADMIN_ID = 12345678  # ضع هنا الأيدي الخاص بك

# إعداد السجلات
logging.basicConfig(level=logging.INFO)

# تشغيل البوت
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# 1. رسالة الترحيب (Start)
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    welcome_text = (
        "💹 **نبض الأسهم الأمريكية**\n\n"
        "المساعد الذكي للتداول في السوق الأمريكي 🇺🇸\n"
        "🔍 **تحليل شرعي** | 📈 **فني** | 📊 **مالي**\n\n"
        "✍️ اكتب رمز السهم مثال `AAPL` او الصندوق مثال `SMH` ويظهر لك التقرير فورًا!"
    )
    await message.reply(welcome_text, parse_mode='Markdown')

# 2. استقبال رموز الأسهم (مثل AAPL)
@dp.message_handler()
async def stock_request(message: types.Message):
    stock_symbol = message.text.upper()
    
    # هنا لاحقاً سنضيف كود الربط مع Alpaca لجلب السعر الحقيقي
    await message.reply(f"🔍 جاري استخراج تقرير لـ: {stock_symbol}...\n⏳ هذه الميزة قيد التطوير للربط مع API.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
