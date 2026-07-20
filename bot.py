import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiohttp import web
import asyncpg
from datetime import datetime

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
DATABASE_URL = os.getenv("DATABASE_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# Стан для введення метрик дня
class MetricsState(StatesGroup):
    waiting_for_muscle_ups = State()

# Ініціалізація бази даних
async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS daily_metrics (
            id SERIAL PRIMARY KEY,
            date DATE UNIQUE NOT NULL,
            muscle_ups INTEGER DEFAULT 0,
            is_clean BOOLEAN DEFAULT TRUE
        );
    ''')
    await conn.close()
    logging.info("Базу даних успішно ініціалізовано.")

# --- ОБМАНКА ДЛЯ RENDER ---
async def handle_ping(request):
    return web.Response(text="AZЪ System Online")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# --- МЕНЮ ---
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
        return
    welcome_text = (
        "🔮 **СИСТЕМА AZЪ | АКТИВАЦІЯ**\n\n"
        "Вітаю, Творцю. Радник та інструмент трансформації реальності готовий до роботи.\n"
        "Тут немає місця слабкості — лише чіткий вектор, дисципліна та аналіз стану."
    )
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

# Логіка введення метрик дня
@dp.message(lambda message: message.text == "📊 Метрики дня")
async def start_metrics_input(message: types.Message, state: FSMContext):
    if str(message.from_user.id) != ADMIN_ID:
        return
    await message.answer("Введіть кількість чистих виходів силою на барах за сьогодні:")
    await state.set_state(MetricsState.waiting_for_muscle_ups)

@dp.message(MetricsState.waiting_for_muscle_ups)
async def save_metrics(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Будь ласка, введіть числове значення.")
        return
    
    count = int(message.text)
    today = datetime.now().date()
    
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        INSERT INTO daily_metrics (date, muscle_ups, is_clean)
        VALUES ($1, $2, TRUE)
        ON CONFLICT (date) 
        DO UPDATE SET muscle_ups = $2;
    ''', today, count)
    await conn.close()
    
    await state.clear()
    await message.answer(f"✅ Результат зафіксовано: **{count}** чистих виходів. Матриця оновлена.", parse_mode="Markdown", reply_markup=get_main_keyboard())

# Модуль аналізу стану та психології
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

# --- АНАЛІТИКА ---
@dp.message(lambda message: message.text == "📈 Аналітика Волі")
async def show_analytics(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow('SELECT SUM(muscle_ups) as total, COUNT(*) as days FROM daily_metrics;')
    await conn.close()
    
    total_ups = row['total'] if row and row['total'] else 0
    days = row['days'] if row and row['days'] else 0
    
    analytics_text = (
        "📊 **АНАЛІТИКА МАТРИЦІ AZЪ**\n\n"
        f"• **Днів у структурі дисципліни:** {days}\n"
        f"• **Сумарно виконано виходів:** {total_ups}\n"
        "• **Слово Творця (Чистота):** Збережено безкомпромісно.\n\n"
        "Кожен день внеску наближає базу вибухової сили до абсолютного максимуму."
    )
    await message.answer(analytics_text, parse_mode="Markdown")

# Планувальник
async def send_morning_message():
    try:
        text = (
            "🔮 **МАТРИЦЯ ВОЛІ | AZЪ**\n\n"
            "* **Слово Творця (Чистота від алкоголю):** Виконується безкомпромісно.\n"
            "* **Стабільна база вибухової сили:** Прагнення до ідеальної техніки.\n\n"
            "Новий день. Нова ітерація дисципліни."
        )
        await bot.send_message(chat_id=ADMIN_ID, text=text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Помилка надсилання: {e}")

async def send_evening_message():
    try:
        await bot.send_message(
            chat_id=ADMIN_ID, 
            text="🌙 **AZЪ | ВЕЧІРНІЙ ЗВІТ**\n\nЧас зафіксувати результати дня. Натисни «📊 Метрики дня» та внеси свої чисті виходи силою.",
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Помилка надсилання: {e}")

scheduler.add_job(send_morning_message, "cron", hour=8, minute=0)
scheduler.add_job(send_evening_message, "cron", hour=21, minute=30)

async def main():
    await init_db()
    await start_web_server()
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
