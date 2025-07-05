# chatgpt_handler.py

import openai
from sheets_handler import get_table_data

def load_prompt():
    try:
        with open("prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "Ты помощник. Промпт не загружен."

async def generate_response(user_question: str) -> str:
    table_data = get_table_data()
    prompt_base = load_prompt()

    prompt = f"""{prompt_base}

Вопрос пользователя: "{user_question}"

Данные таблицы:
{table_data}
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка от OpenAI: {e}"
