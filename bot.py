import os
import anthropic
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": user_text}]
    )
    
    reply = response.content[0].text
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
```

8. Нажми **Cmd + S** чтобы сохранить

---

# 📄 Шаг 15: Создаём файл `requirements.txt`

> Это список "ингредиентов" — библиотек которые нужны боту для работы. Railway читает этот файл и сам всё устанавливает.

1. Снова нажми **"New File"** в VS Code
2. Назови: `requirements.txt`
3. Вставь внутрь **только эти две строчки:**
```
anthropic
python-telegram-bot
```

4. Нажми **Cmd + S**

---

> ✅ Теперь в твоей папке `my-claude-bot` должно быть **ровно 2 файла:**
```
my-claude-bot/
├── bot.py
└── requirements.txt
```

Так выглядит папка в VS Code:
```
EXPLORER
📁 MY-CLAUDE-BOT
   📄 bot.py
   📄 requirements.txt
```

---

# 🐙 Шаг 16–18: Загружаем на GitHub

> GitHub — это как Google Drive, но для кода. Railway будет брать код именно оттуда.

**Шаг 16. Создай аккаунт на GitHub**
1. Зайди на [github.com](https://github.com)
2. Нажми **"Sign up"**
3. Введи email, придумай пароль и username
4. Подтверди email

**Шаг 17. Создай репозиторий (папку для кода)**
1. После входа нажми зелёную кнопку **"New"** (или плюсик вверху справа → "New repository")
2. В поле **"Repository name"** напиши: `my-claude-bot`
3. Выбери **"Public"**
4. Нажми зелёную кнопку **"Create repository"**

**Шаг 18. Загрузи файлы**
1. На странице репозитория найди ссылку **"uploading an existing file"** и нажми на неё
2. Перетащи оба файла (`bot.py` и `requirements.txt`) в окно браузера
3. Подожди пока они загрузятся — увидишь их имена на странице
4. Внизу нажми зелёную кнопку **"Commit changes"**

✅ Готово — твой код теперь на GitHub!

---

# 🚂 Шаг 19–23: Деплоим на Railway

**Шаг 19. Создай аккаунт на Railway**
1. Зайди на [railway.app](https://railway.app)
2. Нажми **"Login"** → **"Login with GitHub"**
3. Разреши Railway доступ к GitHub — нажми **"Authorize"**

**Шаг 20. Создай проект**
1. Нажми **"New Project"**
2. Выбери **"Deploy from GitHub repo"**
3. В списке найди `my-claude-bot` и нажми на него
4. Railway начнёт загружать твой код

**Шаг 21. Подожди сборку (~1-2 минуты)**

Ты увидишь логи — строчки текста которые бегут вниз. Это нормально, Railway устанавливает библиотеки из `requirements.txt`. Жди пока не появится что-то вроде `✅ Build successful`

**Шаг 22. Добавь секретные ключи**

> ⚠️ Это самый важный шаг! Без ключей бот не знает ни кто он, ни к чему подключаться.

1. Нажми на свой проект
2. Сверху найди вкладку **"Variables"**
3. Нажми **"New Variable"** и добавь первую:
   - **Name:** `TELEGRAM_TOKEN`
   - **Value:** вставь токен от BotFather (тот что сохранял в блокнот)
4. Нажми **"Add"**
5. Снова **"New Variable"** и добавь вторую:
   - **Name:** `ANTHROPIC_API_KEY`
   - **Value:** вставь ключ с console.anthropic.com
6. Нажми **"Add"**

**Шаг 23. Railway сам перезапустится** — подожди ~30 секунд

---

# 🟢 Шаг 24: Проверяем бота!

1. Открой Telegram
2. В поиске введи username своего бота (тот что придумал с `_bot` на конце)
3. Нажми **"Start"**
4. Напиши любое сообщение, например:
```
Привет! Кто ты?