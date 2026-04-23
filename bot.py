import os, logging, asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# الإعدادات المتقدمة
API_TOKEN = os.getenv('TELEGRAM_TOKEN')
WEBHOOK_HOST = f"https://{os.getenv('RAILWAY_STATIC_URL')}"
WEBHOOK_PATH = f'/webhook/{API_TOKEN}'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
PORT = int(os.getenv('PORT', 8080))

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- لوحة الأزرار العصرية ---
def get_modern_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # صف الحساب واللغة (عربي/إنجليزي مدمج)
    keyboard.add(
        InlineKeyboardButton("👤 حسابي | My Acc", callback_data="acc"),
        InlineKeyboardButton("🌍 العربية / EN", callback_data="switch_lang")
    )
    
    # صف القنوات بتصميم أيقونات واضحة
    keyboard.add(
        InlineKeyboardButton("➕ إضافة قناة", callback_data="add_ch"),
        InlineKeyboardButton("📋 قنواتي", callback_data="my_ch")
    )
    
    # صف الخدمات التقنية (ويب هوك ورمز الأمان)
    keyboard.add(
        InlineKeyboardButton("🔗 Webhook", callback_data="webk"),
        InlineKeyboardButton("🔐 رمز الأمان", callback_data="token")
    )
    
    # صف التداول والأسهم (الميزات الجديدة)
    keyboard.add(
        InlineKeyboardButton("📉 مؤشر الأسهم", callback_data="idx"),
        InlineKeyboardButton("💰 سعر سهم", callback_data="price")
    )
    
    # صف الدعم والتداول الآلي
    keyboard.add(
        InlineKeyboardButton("🤖 التداول الآلي", callback_data="auto"),
        InlineKeyboardButton("🛠️ الدعم الفني", callback_data="supp")
    )
    
    return keyboard

# --- معالجة الأوامر ---
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    welcome_msg = (
        "💎 **Mr.MOH Bot v2.0**\n"
        "مرحباً بك في المنصة الذكية للتحليل والتداول.\n"
        "━━━━━━━━━━━━━━\n"
        "الآن يمكنك إدارة قنواتك ومتابعة الأسهم بضغطة زر."
    )
    await message.reply(welcome_msg, reply_markup=get_modern_keyboard(), parse_mode="Markdown")

@dp.callback_query_handler(lambda c: True)
async def process_callback(c: types.CallbackQuery):
    # استجابة فورية لإنهاء حالة الانتظار في الزر
    await bot.answer_callback_query(c.id)
    
    user_id = c.from_user.id
    if c.data == "switch_lang":
        await bot.send_message(user_id, "🌐 تم ضبط التفضيلات: **العربية والإنجليزية** نشطة الآن.")
    elif c.data == "webk":
        await bot.send_message(user_id, f"🔗 **رابط الويب هوك الخاص بك:**\n`{WEBHOOK_HOST}/hook/{user_id}`")
    elif c.data == "acc":
        await bot.send_message(user_id, "👤 **بيانات الحساب:**\nالاسم: " + c.from_user.full_name + "\nالحالة: متصل ✅")
    else:
        await bot.send_message(user_id, "⚙️ جاري معالجة طلبك...")

# --- إعدادات التشغيل الويب هوك ---
async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook set to: {WEBHOOK_URL}")

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
