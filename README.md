# Mention Monitor 2.0

Система автоматического мониторинга и парсинга упоминаний по ключевым словам из социальных сетей, мессенджеров, Telegram-каналов и веб-сайтов, включая анализ Stories.

---

## Возможности

| Функция | Статус |
|---|---|
| Парсинг VK (посты + Stories) | ✅ |
| Парсинг Max (web-scraping) | ✅ |
| Парсинг TenChat (посты + Stories) | ✅ |
| Парсинг Telegram (Telethon) | ✅ |
| Парсинг веб-сайтов (BeautifulSoup) | ✅ |
| Парсинг динамических сайтов (Selenium) | ✅ |
| Краулинг сайтов (Scrapy) | ✅ |
| Ключевые слова с AND/OR и exact match | ✅ |
| Минус-слова | ✅ |
| Белый / Чёрный список источников | ✅ |
| Приоритеты источников (1–10) | ✅ |
| Чёрный / Белый список пользователей | ✅ |
| Геофильтрация (страна / город) | ✅ |
| Фильтр по времени (24ч / 3д / неделя / произвольный) | ✅ |
| **Исторический поиск** | ✅ |
| OCR текста из изображений (Tesseract) | ✅ |
| AI-анализ изображений (Google Vision / OpenCV) | ✅ |
| Распознавание контекста ("ищу квартиру") | ✅ |
| Экспорт CSV / Excel / JSON | ✅ |
| CRM-интеграция (amoCRM, Bitrix24) через Webhook | ✅ |
| Celery + Redis (очереди задач, 24/7) | ✅ |
| Docker Compose (полный деплой) | ✅ |
| Документация (README) | ✅ |

---

## Быстрый старт

### 1. Клонировать / распаковать репозиторий

```bash
git clone <repo-url> mention_monitor
cd mention_monitor
```

### 2. Настроить переменные окружения

```bash
cp backend/.env.example backend/.env
# Отредактируйте backend/.env и укажите токены
```

Минимально необходимые переменные:

```env
# Обязательно
DATABASE_URL=postgresql://admin:admin@db/mention_monitor
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-here

# VK (для парсинга ВКонтакте)
VK_ACCESS_TOKEN=your_vk_token

# Telegram (для парсинга Telegram-каналов)
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+79001234567

# Google Vision API (опционально, для AI-анализа изображений)
GOOGLE_APPLICATION_CREDENTIALS=/app/creds/google_vision.json

# Частота парсинга (минуты, 5–60)
PARSER_INTERVAL=15
```

### 3. Запустить через Docker Compose

```bash
docker compose up -d
```

Сервисы:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Selenium Grid**: http://localhost:4444

### 4. Запуск без Docker (разработка)

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Celery Worker
celery -A workers.celery_app worker --loglevel=info

# Celery Beat (планировщик)
celery -A workers.celery_app beat --loglevel=info

# Frontend
cd ../frontend
npm install
npm run dev
```

---

## Архитектура

```
mention_monitor/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI роутеры
│   │   │   ├── keywords.py        # Ключевые слова
│   │   │   ├── sources.py         # Источники + приоритеты
│   │   │   ├── filters.py         # Пользователи (ЧС/БС)
│   │   │   ├── results.py         # Результаты + экспорт
│   │   │   ├── settings.py        # Настройки парсера
│   │   │   ├── integrations.py    # CRM webhooks
│   │   │   └── historical.py      # Исторический поиск
│   │   ├── services/
│   │   │   ├── parser_manager.py  # Оркестрация парсеров
│   │   │   ├── filter_engine.py   # Фильтрация результатов
│   │   │   └── export_service.py  # CSV / Excel / JSON
│   │   └── utils/
│   │       ├── ocr.py             # Tesseract OCR
│   │       ├── ai_vision.py       # Google Vision / OpenCV
│   │       └── geo.py             # Геолокация из текста
│   ├── parsers/
│   │   ├── base_parser.py         # Базовый класс
│   │   ├── web_parser.py          # Статические сайты (BS4)
│   │   ├── selenium_web_parser.py # Динамические сайты (Selenium)
│   │   ├── scrapy_spider.py       # Краулинг (Scrapy)
│   │   ├── vk_parser.py           # VK API + Stories
│   │   ├── max_parser.py          # Max (web scraping)
│   │   ├── tenchat_parser.py      # TenChat + Stories
│   │   ├── telegram_parser.py     # Telegram (Telethon)
│   │   └── story_processor.py     # Обработка Stories (OCR + AI)
│   └── workers/
│       ├── celery_app.py          # Celery конфигурация
│       ├── parse_tasks.py         # Периодические задачи
│       └── ocr_tasks.py           # OCR задачи
├── frontend/                      # React интерфейс
└── docker-compose.yml             # Полный деплой
```

---

## API Reference

Полная документация: http://localhost:8000/docs

### Основные эндпоинты

| Метод | URL | Описание |
|---|---|---|
| GET | `/api/results` | Список упоминаний с фильтрами |
| GET | `/api/results/export?format=csv` | Экспорт (csv/excel/json) |
| GET/POST | `/api/keywords` | Управление ключевыми словами |
| GET/POST | `/api/sources` | Управление источниками |
| PATCH | `/api/sources/{id}/priority` | Приоритет источника |
| GET/POST | `/api/integrations` | CRM-интеграции |
| POST | `/api/historical/search` | Исторический поиск |
| POST | `/api/settings/run_now` | Запустить парсинг вручную |

### Исторический поиск

```bash
curl -X POST http://localhost:8000/api/historical/search \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["квартира", "аренда"],
    "date_from": "2025-01-01T00:00:00",
    "date_to": "2025-06-01T00:00:00",
    "source_types": ["vk", "telegram"],
    "channels": ["realtor_moscow", "realty_spb"]
  }'
```

---

## Источники данных

| Источник | Метод | Требует токен |
|---|---|---|
| VK | Official API | ✅ VK_ACCESS_TOKEN |
| VK Stories | Official API | ✅ VK_ACCESS_TOKEN |
| Max | Web scraping | ❌ |
| TenChat | Web scraping | ❌ |
| TenChat Stories | Web scraping | ❌ |
| Telegram | Telethon API | ✅ TELEGRAM_API_ID + HASH + PHONE |
| Веб-сайты (статика) | BeautifulSoup | ❌ |
| Веб-сайты (динамика) | Selenium | ❌ (нужен Selenium Grid) |
| Краулинг | Scrapy | ❌ |

---

## Stories и AI-анализ

Система автоматически обрабатывает Stories из VK и TenChat:

1. **Извлечение текста** — встроенный текст из API
2. **OCR** — Tesseract распознаёт наложенный текст с изображений (разные шрифты, наклон, перекрытие)
3. **AI-анализ** — Google Vision API или OpenCV:
   - Распознавание объектов
   - Выявление контекста: "ищу квартиру", "поиск специалиста", "мероприятие/событие" и др.
   - Определение доминирующих цветов, лиц, текстовых областей

---

## Приоритеты источников

Приоритет задаётся при создании источника (поле `priority`, 1–10):
- **10** — наивысший (парсится первым)
- **1** — наинизший
- **5** — по умолчанию

Парсеры обрабатывают whitelist-URL в порядке убывания приоритета.

---

## CRM-интеграции

Поддерживаются amoCRM и Bitrix24 через Webhook.

```bash
# Добавить интеграцию
curl -X POST http://localhost:8000/api/integrations/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "amocrm",
    "webhook_url": "https://yourdomain.amocrm.ru/api/v4/leads",
    "is_active": true,
    "send_on_types": ["text", "story", "image"]
  }'

# Тест
curl -X POST http://localhost:8000/api/integrations/1/test
```

---

## Требования

- Docker + Docker Compose **или** Python 3.11+, Node.js 20+
- PostgreSQL 15+
- Redis 7+
- Tesseract OCR (`apt install tesseract-ocr tesseract-ocr-rus`)
- Chrome/Chromium (для Selenium)
