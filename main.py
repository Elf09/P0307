# main.py

import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from chatgpt_handler import generate_response
import openai

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

application = Application.builder().token(TELEGRAM_TOKEN).build()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await application.initialize()
    yield

app = FastAPI(lifespan=lifespan)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, Кристина! Бот работает 🎉")

# Сообщения
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text
    reply = await generate_response(user_question)
    await update.message.reply_text(reply)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Webhook
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
