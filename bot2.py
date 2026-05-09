import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ====== ТОКЕНЫ ======
TELEGRAM_TOKEN = "8633826553:AAFxU9MVBEy4E_M4ZcS8s5z2v9E0iFpbewU"
OPENROUTER_API_KEY = "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"

# ====== ПАМЯТЬ ДИАЛОГА ======
user_memory = {}

# ====== МЕНЮ ======
keyboard = [
    ["💬 Чат", "🧹 Очистить память"],
    ["ℹ️ О боте"]
]

markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ====== AI ======
def ask_ai(user_id, prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"

    if user_id not in user_memory:
        user_memory[user_id] = []

    # добавляем сообщение пользователя
    user_memory[user_id].append({"role": "user", "content": prompt})

    # ограничим память (чтобы не раздувалось)
    user_memory[user_id] = user_memory[user_id][-10:]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [
            {
                "role": "system",
                "content": "Ты умный помощник как ChatGPT. Отвечай по-русски, понятно и полезно."
            }
        ] + user_memory[user_id]
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=20)
        result = response.json()

        if "error" in result:
            return f"Ошибка API: {result['error']['message']}"

        answer = result["choices"][0]["message"]["content"]

        # сохраняем ответ AI в память
        user_memory[user_id].append({"role": "assistant", "content": answer})

        return answer

    except Exception as e:
        return f"Ошибка соединения: {str(e)}"


# ====== START ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет 👋 Я AI-ассистент как ChatGPT",
        reply_markup=markup
    )


# ====== MESSAGE ======
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.chat_id

    if text == "💬 Чат":
        await update.message.reply_text("Напиши любой вопрос 👇")

    elif text == "🧹 Очистить память":
        user_memory[user_id] = []
        await update.message.reply_text("Память очищена 🧠")

    elif text == "ℹ️ О боте":
        await update.message.reply_text("🤖 Это AI бот с памятью, как ChatGPT")

    else:
        await update.message.reply_text("Думаю... 🤖")
        answer = ask_ai(user_id, text)
        await update.message.reply_text(answer)


# ====== RUN ======
app = Application.builder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot running...")
app.run_polling()