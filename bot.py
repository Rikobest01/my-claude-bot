import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
import anthropic
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def get_youtube_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

def get_youtube_transcript(url):
    try:
        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["ru", "en"],
            "subtitlesformat": "json3",
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            subtitles = info.get("subtitles") or info.get("automatic_captions") or {}
            lang = None
            if "ru" in subtitles:
                lang = "ru"
            elif "en" in subtitles:
                lang = "en"
            elif subtitles:
                lang = list(subtitles.keys())[0]
            if not lang:
                return None
            sub_data = subtitles[lang]
            for fmt in sub_data:
                if fmt.get("ext") == "json3":
                    sub_url = fmt["url"]
                    response = requests.get(sub_url, timeout=10)
                    data = response.json()
                    texts = []
                    for event in data.get("events", []):
                        for seg in event.get("segs", []):
                            t = seg.get("utf8", "").strip()
                            if t and t != "\n":
                                texts.append(t)
                    return " ".join(texts)[:6000]
        return None
    except Exception as e:
        return f"ОШИБКА: {str(e)}"

def analyze_website(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return text[:5000]
    except Exception as e:
        return f"Ошибка при загрузке сайта: {e}"

def read_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        return df.to_string(index=False)[:5000]
    except Exception as e:
        return f"Ошибка при чтении файла: {e}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    youtube_match = re.search(r"(https?://(?:www\.)?(?:youtube\.com/watch\S+|youtu\.be/\S+))", user_text)

    if youtube_match:
        url = youtube_match.group(1)
        task = user_text.replace(url, "").strip()
        if not task:
            task = "сделай полный анализ видео: о чём оно, главные идеи списком, лучшие моменты для Reels с таймингами, самая сильная цитата"
        await update.message.reply_text("Читаю субтитры видео, подожди...")
        transcript = get_youtube_transcript(url)
        if transcript and not transcript.startswith("ОШИБКА"):
            prompt = f"""Ты эксперт по контент-маркетингу. Вот субтитры YouTube видео.\n\nЗадание пользователя: {task}\n\nСубтитры:\n{transcript}"""
        else:
            await update.message.reply_text(f"Не удалось получить субтитры: {transcript}")
            return

    elif user_text.startswith("http://") or user_text.startswith("https://"):
        await update.message.reply_text("Анализирую сайт, подожди...")
        site_content = analyze_website(user_text)
        prompt = f"Проанализируй этот сайт и дай краткое резюме: что это за компания, чем занимается, контакты если есть.\n\n{site_content}"

    else:
        prompt = user_text

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}]
    )
    reply = response.content[0].text
    await update.message.reply_text(reply)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    file_name = file.file_name
    if not (file_name.endswith(".xlsx") or file_name.endswith(".xls") or file_name.endswith(".csv")):
        await update.message.reply_text("Отправь файл в формате Excel (.xlsx, .xls) или CSV")
        return
    await update.message.reply_text("Читаю файл, подожди...")
    tg_file = await context.bot.get_file(file.file_id)
    file_path = f"/tmp/{file_name}"
    await tg_file.download_to_drive(file_path)
    if file_name.endswith(".csv"):
        df = pd.read_csv(file_path)
        data_text = df.to_string(index=False)[:5000]
    else:
        data_text = read_excel(file_path)
    prompt = f"Ты аналитик продаж. Проанализируй эти данные и дай краткий отчёт: основные выводы, топ позиции, на что обратить внимание.\n\n{data_text}"
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}]
    )
    reply = response.content[0].text
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
app.run_polling()
