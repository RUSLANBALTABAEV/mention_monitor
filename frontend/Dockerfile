# ====================== STAGE 1: Сборка ======================
FROM node:20-alpine AS builder

WORKDIR /app

# Копируем package.json и устанавливаем зависимости
COPY package*.json ./
RUN npm ci --only=production

# Копируем весь исходный код
COPY . .

# Собираем production-билд
RUN npm run build

# ====================== STAGE 2: Продакшн (Nginx) ======================
FROM nginx:alpine

# Копируем собранный билд из первого stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Копируем конфиг nginx (опционально, если нужен кастом)
COPY nginx.conf /etc/nginx/conf.d/default.conf 2>/dev/null || true

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
