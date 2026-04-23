# استخدام نسخة بايثون خفيفة ومستقرة
FROM python:3.11-slim

# تثبيت مكتبات النظام اللازمة لتشغيل matplotlib والرسوم البيانية
RUN apt-get update && apt-get install -y \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# نسخ وتثبيت المكتبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع (تأكد أن bot.py الجديد موجود في نفس المجلد)
COPY . .

# إخبار Railway بالمنفذ الذي سيعمل عليه الويب هوك
ENV PORT=8080
EXPOSE 8080

# تشغيل البوت
CMD ["python", "bot.py"]
