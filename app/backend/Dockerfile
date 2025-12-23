# نستخدم نسخة بايثون خفيفة
FROM python:3.10-slim

# نحدد فولدر الشغل
WORKDIR /app

# مكتبات السيستم
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# --- التعديل هنا ---
# ضفنا --default-timeout=1000 عشان يستحمل النت البطيء (1000 ثانية بدل 15)
# وضفنا --no-cache-dir عشان مياخدش مساحة على الفاضي
RUN pip install --default-timeout=1000 --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 1. ننسخ ملف المتطلبات
COPY requirements.txt .

# 2. ننزل باقي المكاتب (برضو زودنا التايم اوت هنا احتياطي)
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# 3. ننسخ باقي ملفات الكود
COPY . .

# نفتح بورت 8000
EXPOSE 8000

# أمر التشغيل
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]