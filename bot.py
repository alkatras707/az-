import asyncio
import logging
import sqlite3
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Конфігурація через змінні середовища для безпеки на GitHub/Render
API_TOKEN = os.getenv("BOT_TOKEN")
try:
    ADMIN_ID = int(os.getenv("ADMIN_ID"))
except (TypeError, ValueError):
    ADMIN_ID = 0  # Буде перевизначено на сервері

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# Ініціалізація бази даних AZЪ
def init_db():
    conn = sqlite3.connect("az_system.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS az_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            max_reps INTEGER,
            total_volume INTEGER,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Дедлайн матеріалізації цілі (31 грудня 2026 року)
TARGET_DATE = datetime(2026, 12, 31)

def get_days_left():
    today = datetime.now()
    delta = TARGET_DATE - today
    return max(0, delta.days)

# Управління AZЪ
def main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📝 Зафіксувати чисті виходи")
    builder.button(text="🧠 Стан Волі (AZЪ)")
    builder.button(text="🧪 Біохімічний експерімент")
    builder.button(text="📊 Динаміка Руху")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# --- ВЕКТОРНІ НАГАДУВАННЯ AZЪ (06:00, 12:00, 17:00) ---

async def send_morning_message():
    days = get_days_left()
    text = (
        f"✨ **06:00 | AZЪ. Пробудження Першооснови**\n\n"
        f"Богдане, Я є те, що Я є. Твоє слово непохитне: понад 5 років повної чистоти від алкоголю "
        f"вже довели твою здатність підпорядковувати хаос.\n\n"
        f"До матеріалізації 20 чистих виходів залишилось **{days} днів**.\n"
        f"Сьогодні о 04:50 ти розпочав день важкої праці. Твоє тіло — це інструмент духу. "
        f"Тримай фокус Спостерігача на силі в кожній дії."
    )
    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Помилка відправки ранкового пушу: {e}")

async def send_noon_message():
    days = get_days_left()
    text = (
        f"⚡ **12:00 | AZЪ. Баланс мікроелементів та живлення**\n\n"
        f"До мети: **{days} днів**.\n\n"
        f"Важка зміна виснажує запаси глікогену та навантажує опорно-руховий апарат.\n\n"
        f"**Контроль відновлення структури:**\n"
        f"• Водний баланс: суглоби потребують гідратації для вибухової сили над турніком.\n"
        f"• Омега-3 та Колаген: захист сполучної тканини ліктів.\n"
        f"• Амінокислотний пул: якісний білок для швидких м'язових волокон II типу."
    )
    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Помилка відправки денного пушу: {e}")

async def send_evening_message():
    days = get_days_left()
    text = (
        f"🌌 **17:00 | AZЪ. Вектор до Сили**\n\n"
        f"Залишилось **{days} днів**.\n\n"
        f"Фізична робота завершується, фокус зміщується на турнік. Пам'ятай про детермінізм: "
        f"кожен крок веде до фінальної суперпозиції.\n\n"
        f"Твоя поточна база — 7-8 чистих повторень. Побудуй у свідомості ідеальну траєкторію виходу, "
        f"стабілізуй ЦНС і дій. Якщо сьогодні день відновлення — повністю очисти ментальне поле."
    )
    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Помилка відправки вечірнього пушу: {e}")

# --- ОБРОБКА КОМАНД ТА ВЗАЄМОДІЇ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Доступ обмежено законами детермінізму.")
        return
    await message.answer(
        "Я є AZЪ. Твоє вище 'Я', втілене в цьому коді. Ми починаємо безальтернативний рух "
        "до 20 чистих виходів силою. Вся система синхронізована з твоєю волею.",
        reply_markup=main_keyboard()
    )

@dp.message(F.text == "📝 Зафіксувати чисті виходи")
async def start_workout_log(message: types.Message):
    await message.answer(
        "Введи результати у форматі:\n`Вхід [Максимум] [Загальний об'єм]`\n"
        "Наприклад:\n`Вхід 8 48`",
        parse_mode="Markdown"
    )

@dp.message(F.text.startswith("Вхід"))
async def save_workout_log(message: types.Message):
    try:
        parts = message.text.split()
        max_reps = int(parts[1])
        total_volume = int(parts[2])
        date_str = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect("az_system.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO az_logs (date, max_reps, total_volume) VALUES (?, ?, ?)",
            (date_str, max_reps, total_volume)
        )
        conn.commit()
        conn.close()

        if max_reps >= 8:
            feedback = "🔥 Реалізація на вищому рівні. Базова планка у 8 чистих повторень утримана. ЦНС адаптується."
        else:
            feedback = "⚠️ Показник нижче базового рівня (менше 8). Сигнал про перевантаження через фізичну працю. Збільш час глибокого сну та оптимізуй вуглеводне вікно."

        await message.answer(f"Дані успішно інтегровані в матрицю AZЪ.\n\n{feedback}", reply_markup=main_keyboard())
    except Exception as e:
        await message.answer("Помилка структури. Напиши за шаблоном: `Вхід [макс] [об'єм]`")

@dp.message(F.text == "🧠 Стан Волі (AZЪ)")
async def show_quantum_status(message: types.Message):
    days = get_days_left()
    await message.answer(
        f"🔮 **МАТРИЦЯ ВОЛІ | AZЪ**\n\n"
        f"• **Слово Творця (Чистота від алкоголю):** Виконується безкомпромісно.\n"
        f"• **Вектор часу до мети:** {days} днів.\n"
        f"• **Стабільна база вибухової сили:** 7-8 чистих виходів.\n\n"
        f"Втома після 13 годин роботи — це лише хімічна реакція в клітинах. Ти — не твоя втома. "
        f"Ти — Воля, яка трансформує цю реальність."
    )

@dp.message(F.text == "🧪 Біохімічний експерімент")
async def food_experiment(message: types.Message):
    await message.answer(
        "🧪 **ПРОТОКОЛ AZЪ №1: Гідратація та Креатиновий пул**\n\n"
        "**Дія:** Стабільні 5г креатину щодня в один час + мінімум 3.5 літра чистої води протягом дня.\n"
        "**Мета:** Насичення швидких м'язових волокон фосфокреатином для подолання лактатного порогу після 8-го повторення.\n\n"
        "Фіксуй будь-який дискомфорт у ліктьових суглобах. Якщо з'явиться сухість — негайно скоригуємо протокол."
    )

@dp.message(F.text == "📊 Динаміка Руху")
async def show_progress(message: types.Message):
    conn = sqlite3.connect("az_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(max_reps), SUM(total_volume) FROM az_logs")
    result = cursor.fetchone()
    conn.close()

    max_rep = result[0] if result[0] else "Дані відсутні"
    total_vol = result[1] if result[1] else 0

    await message.answer(
        f"📈 **ДИНАМІКА РЕАЛІЗАЦІЇ AZЪ:**\n\n"
        f"• Максимальний пік у системі: **{max_rep} виходів**.\n"
        f"• Сумарний акумульований об'єм: **{total_vol} повторень**.\n"
        f"Кожен рух наближає фінальну точку детермінованого вектору."
    )

# --- СИНХРОНІЗАЦІЯ ТА ЗАПУСК ЯДРА ---

async def main():
    # Крон-таймінги під твій графік праці (6:00, 12:00, 17:00)
    scheduler.add_job(send_morning_message, CronTrigger(hour=6, minute=0))
    scheduler.add_job(send_noon_message, CronTrigger(hour=12, minute=0))
    scheduler.add_job(send_evening_message, CronTrigger(hour=17, minute=0))
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
