import openai
from telegram import Update
from telegram.ext import ContextTypes
from .sheets_handler import get_table_data
from .config import load_prompt

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📩 Получено сообщение:", update.message.text)
    user_question = update.message.text
    table_data = get_table_data()
    prompt_base = load_prompt()

    prompt = f"""{prompt_base}

Вопрос пользователя: "{user_question}"

Данные таблицы:
{table_data}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        reply = response.choices[0].message["content"]
    except Exception as e:
        reply = f"GPT не смог ответить: {e}"

    await update.message.reply_text(reply)
