# --- المرحلة الأولى: البناء (Builder Stage) ---
FROM node:18-alpine AS builder

# نحدد فولدر الشغل جوه الكونتينر
WORKDIR /app

# 1. ننسخ ملفات الـ package من جوه فولدر void-landing
COPY void-landing/package*.json ./

# 2. ننزل المكاتب
RUN npm install

# 3. ننسخ باقي ملفات الكود
COPY void-landing/ .

# 4. نبني المشروع (Vite هيطلع فولدر اسمه dist)
RUN npm run build

# --- المرحلة الثانية: السيرفر (Production Stage) ---
FROM nginx:alpine

# هنا استخدمنا dist عشان مشروعك Vite
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
