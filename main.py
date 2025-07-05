import os
import json
import base64
import uvicorn
import gspread
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from google.oauth2.service_account import Credentials
from openai import OpenAI
from sheets_handler import get_table_data

# Получаем токены из переменных среды
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CREDS_BASE64 = os.getenv("GOOGLE_CREDS_BASE64")

# Проверка токена Telegram
if not TELEGRAM_TOKEN:
    raise Exception("❌ TELEGRAM_TOKEN пуст — проверь переменные Railway!")

# Настройка OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Настройка Google Sheets
creds = None
sheet = None
if GOOGLE_CREDS_BASE64:
    creds_dict = json.loads(base64.b64decode(GOOGLE_CREDS_BASE64))
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client_sheet = gspread.authorize(creds)
    sheet = client_sheet.open_by_key(SPREADSHEET_ID).sheet1

# Создаём Telegram-приложение
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Lifespan для запуска
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Инициализация Telegram-приложения...")
    await application.initialize()
    print("✅ Готов к приёму обновлений")
    yield

# Загрузка промпта из файла
def load_prompt():
    try:
        with open("prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Ты помощник. Промпт не загружен."

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, Кристина! Бот работает 🎉")

# Обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📩 Получено сообщение:", update.message.text)
    user_question = update.message.text
    table_data = sheet.get_all_values() if sheet else [["Нет данных"]]
    prompt_base = load_prompt()

    full_prompt = f"""{prompt_base}

Вопрос пользователя: "{user_question}"

Данные таблицы:
{table_data}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.3,
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"GPT не смог ответить: {e}"

    await update.message.reply_text(reply)

# Подключаем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Создаём FastAPI-приложение
app = FastAPI(lifespan=lifespan)

# Обработчик вебхука
@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return PlainTextResponse("ok")
    except Exception as e:
        print("❌ Ошибка в webhook:", e)
        return PlainTextResponse("error", status_code=500)

# Запуск
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
