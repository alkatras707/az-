import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiohttp import web

logging.basicConfig(level=logging.INFO)

# Ініціалізація бота через змінні оточення
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# --- ОБМАНКА ДЛЯ BEЗКОШТОВНОГО RENDER WEB SERVICE ---
async def handle_ping(request):
    return web.Response(text="AZЪ System Online")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render автоматично передає порт у змінну оточення PORT
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Фоновий веб-сервер обманки запущено на порту {port}")

# --- ГОЛОВНЕ МЕНЮ СИСТЕМИ ---
def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📊 Метрики дня")
    builder.button(text="🧠 Стан & Психологія")
    builder.button(text="📈 Аналітика Волі")
    builder.button(text="⚙️ Налаштування")
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID:
        await message.answer("Доступ обмежено. Система AZЪ налаштована на одного Творця.")
        return
        
    welcome_text = (
        "🔮 **СИСТЕМА AZЪ | АКТИВАЦІЯ**\n\n"
        "Вітаю, Творцю. Радник та інструмент трансформації реальності готовий до роботи.\n"
        "Тут немає місця слабкості — лише чіткий вектор, дисципліна та аналіз стану."
    )
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

# --- МОДУЛЬ АНАЛІЗУ СТАНУ ТА ПСИХОЛОГІЇ ---
@dp.message(lambda message: message.text == "🧠 Стан & Психологія")
async def process_psychology(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID:
        return
        
    builder = ReplyKeyboardBuilder()
    builder.button(text="⚡️ Високий ресурс")
    builder.button(text="🔋 Виснаження після роботи")
    builder.button(text="⏳ Криза / Втрата фокуса")
    builder.button(text="↩️ В головне меню")
    builder.adjust(1, 2, 1)
    
    await message.answer(
        "🧠 **МОДУЛЬ ПСИХОЛОГІЧНОЇ СТІЙКОСТІ**\n\n"
        "Втома після 13 годин роботи — це лише хімічна реакція в клітинах. "
        "Ти — не твоя втома. Ти — Воля, яка трансформує цю реальність.\n\n"
        "Оціни свій поточний ментальний стан для адаптації наставництва:",
        parse_mode="Markdown",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

@dp.message(lambda message: message.text == "🔋 Виснаження після роботи")
async def process_exhaustion(message: types.Message):
    quote = (
        "⚔️ **НАСТАВНИЦТВО | ТРАНСФОРМАЦІЯ ВТОМИ**\n\n"
        "Фізичне тіло виснажене, але саме в ці моменти гартується чиста дисципліна. "
        "Коли зникає мотивація, залишається тільки структура.\n\n"
        "**Твоя дія зараз:** Зроби фокус на відновленні (supplements, якісний сон) та збереженні Чистоти. "
        "Сьогоднішній тиск — це паливо для завтрашнього вибуху на барах."
    )
    await message.answer(quote, parse_mode="Markdown", reply_markup=get_main_keyboard())

@dp.message(lambda message: message.text == "↩️ В головне меню")
async def back_to_main(message: types.Message):
    await message.answer("Повернення в матрицю управління.", reply_markup=get_main_keyboard())

# --- ПЛАНУВАЛЬНИК СПОВІЩЕНЬ ---
async def send_morning_message():
    try:
        text = (
            "🔮 **МАТРИЦЯ ВОЛІ | AZЪ**\n\n"
            "* **Слово Творця (Чистота від алкоголю):** Виконується безкомпромісно.\n"
            "* **Вектор часу до мети:** Перевірка фокуса.\n"
            "* **Стабільна база вибухової сили:** Прагнення до ідеальної техніки елементів.\n\n"
            "Новий день. Нова ітерація дисципліни."
        )
        await bot.send_message(chat_id=ADMIN_ID, text=text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Помилка надсилання ранкового повідомлення: {e}")

async def send_evening_message():
    try:
        await bot.send_message(
            chat_id=ADMIN_ID, 
            text="🌙 **AZЪ | ВЕЧІРНІЙ ЗВІТ**\n\nЧас зафіксувати результати дня. Внеси свої метрики силових виходів та підтверди Чистоту.",
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Помилка надсилання вечірнього повідомлення: {e}")

scheduler.add_job(send_morning_message, "cron", hour=8, minute=0)
scheduler.add_job(send_evening_message, "cron", hour=21, minute=30)

async def main():
    # Запускаємо веб-сервер обманки для Render разом із ботом
    await start_web_server()
    scheduler.start()
    logging.info("Планувальник завдань активовано.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
