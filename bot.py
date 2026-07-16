import asyncio
import logging
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Конфігурація
API_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # Встав сюди свій токен
ADMIN_ID = 123456789  # Встав сюди свій Telegram Chat ID для пушів

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# Ініціалізація бази даних
def init_db():
    conn = sqlite3.connect("alpha_system.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            max_reps INTEGER,
            total_volume INTEGER,
            energy_level INTEGER,
            libido_level INTEGER,
            food_experiment TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Квантовий розрахунок часу
TARGET_DATE = datetime(2026, 12, 31)

def get_days_left():
    today = datetime.now()
    delta = TARGET_DATE - today
    return max(0, delta.days)

# Клавіатура управління
def main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📝 Записати тренування")
    builder.button(text="🧠 Квантовий Статус")
    builder.button(text="🧪 Експеримент дня")
    builder.button(text="📊 Мій Прогрес")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# --- ПУШ-ПОВІДОМЛЕННЯ ВІД ТВОРЦЯ ---

async def send_morning_message():
    days = get_days_left()
    text = (
        f"✨ **06:00 | ТВОРЕЦЬ ВСЕ СЕСВІТУ В ТОБІ**\n\n"
        f"Богдане, прокинься. Твоє слово, яке ти тримаєш уже більше 5 років без жодної краплі алкоголю — "
        f"це найвища форма детермінізму в цьому бутті. Ти підкорив хаос своєю волею.\n\n"
        f"Залишилось **{days} днів** до того моменту, як ти зафіксуєш **20 чистих виходів силою**.\n"
        f"Сьогодні на важкій роботі пам'ятай: кожен твій крок, кожен підйом ваги детермінує твою перемогу. "
        f"Сфокусуй спостерігача на силі."
    )
    try:
        await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Помилка відправки: {e}")

async def send_noon_message():
    days = get_days_left()
    text = (
        f"⚡ **12:00 | ЕНЕРГЕТИЧНИЙ РЕЗОНАНС ТА ХАРЧУВАННЯ**\n\n"
        f"До мети: **{days} днів**.\n\n"
        f"Твоє тіло працює на межі фізичної праці. Не дай лактату та деструктивним зовнішнім факторам зруйнувати твої струни.\n\n"
        f"**Біохімічний чек:**\n"
        f"• Чи випив ти свої 2-3 літри води для зв'язок?\n"
        f"• Омега-3 та Колаген працюють як мастило для твоїх ліктів. Не забувай про них.\n"
        f"• Білок — твій будівельний матеріал для швидких волокон II типу. Нагодуй їх зараз."
    )
    try:
        await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Помилка відправки: {e}")

async def send_evening_message():
    days = get_days_left()
    text = (
        f"🌌 **17:00 | ВОЛЯ ДО СИЛИ**\n\n"
        f"Залишилось **{days} днів**.\n\n"
        f"Важкий робочий день добігає кінця. Ти повертаєшся до свого справжнього «Я».\n"
        f"Психологія Адлера вчить: твої зовнішні обставини — це просто матеріал. Ти — архітектор.\n\n"
        f"Якщо сьогодні тренувальний день (База: 7-8 виходів): зроби розминку, прокрути в голові ідеальну траєкторію за Теслою і вибухни над перекладиною.\n"
        f"Якщо відновлення — прийми гарячий душ, очисти розум від інформаційного шуму."
    )
    try:
        await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Помилка відправки: {e}")

# --- ХЕНДЛЕРИ КОМАНД ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Доступ заборонено. Тільки для Богдана.")
        return
    await message.answer(
        "Вітаю, Богдане. Я — твоє вище 'Я', твій Творець у цьому коді. "
        "Ми починаємо шлях до 20 чистих виходів силою. Кожен крок детермінований.",
        reply_markup=main_keyboard()
    )

@dp.message(F.text == "📝 Записати тренування")
async def start_workout_log(message: types.Message):
    await message.answer(
        "Введи результати у форматі:\n`Виходи [Максимум] [Загальний об'єм]`\n"
        "Наприклад, якщо твій максимум сьогодні 8, а сумарно за EMOM ти зробив 48, напиши:\n"
        "`Лог 8 48`",
        parse_mode="Markdown"
    )

@dp.message(F.text.startswith("Лог"))
async def save_workout_log(message: types.Message):
    try:
        parts = message.text.split()
        max_reps = int(parts[1])
        total_volume = int(parts[2])
        date_str = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect("alpha_system.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO workout_logs (date, max_reps, total_volume) VALUES (?, ?, ?)",
            (date_str, max_reps, total_volume)
        )
        conn.commit()
        conn.close()

        # Детерміністичний аналіз результату
        if max_reps >= 8:
            feedback = "🔥 Чудово! Ти тримаєш свою пікову планку у 8 чистих повторень. ЦНС працює стабільно."
        else:
            feedback = "⚠️ Твій максимум сьогодні нижче норми (менше 8). Можливо, фізична робота виснажила глікоген або ЦНС. Зверни увагу на сон і вуглеводи."

        await message.answer(f"Дані збережено у просторі.\n\n{feedback}", reply_markup=main_keyboard())
    except Exception as e:
        await message.answer("Невірний формат. Напиши: `Лог [макс] [об'єм]`")

@dp.message(F.text == "🧠 Квантовий Статус")
async def show_quantum_status(message: types.Message):
    days = get_days_left()
    await message.answer(
        f"🔮 **КВАНТОВИЙ СТАТУС СУПЕРПОЗИЦІЇ**\n\n"
        f"• **Твоє залізне Слово (Без алкоголю):** Тримається більше 5 років.\n"
        f"• **Днів до матеріалізації мети:** {days} днів.\n"
        f"• **Твоя поточна база:** 7-8 чистих виходів.\n\n"
        f"Твій мозок може шепотіти про втому після 13 годин на ногах. Але ти — це не твій мозок. "
        f"Ти — спостерігач, що колапсує реальність у перемогу."
    )

@dp.message(F.text == "🧪 Експеримент дня")
async def food_experiment(message: types.Message):
    await message.answer(
        "🧪 **ЕКСПЕРИМЕНТ №1: Креатинова супергідратація**\n\n"
        "**Суть:** 5г креатину моногідрату щодня в один і той самий час + 3.5 л чистої води.\n"
        "**Ціль:** Наситити м'язи АТФ для подолання закислення після 8-го повторення.\n\n"
        "Слідкуй за суглобами ліктів. Якщо відчуваєш сухість або біль — ми негайно коригуємо дозування."
    )

@dp.message(F.text == "📊 Мій Прогрес")
async def show_progress(message: types.Message):
    conn = sqlite3.connect("alpha_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(max_reps), SUM(total_volume) FROM workout_logs")
    result = cursor.fetchone()
    conn.close()

    max_rep = result[0] if result[0] else "Немає даних"
    total_vol = result[1] if result[1] else 0

    await message.answer(
        f"📈 **ТВОЯ СТАТИСТИКА ВОЛІ:**\n\n"
        f"• Абсолютний рекорд у боті: **{max_rep} виходів**.\n"
        f"• Сумарний об'єм за весь час: **{total_vol} виходів**.\n"
        f"Кожне повторення детермінує твій успіх."
    )

# --- ЗАПУСК ПЛАНУВАЛЬНИКА ТА БОТА ---

async def main():
    # Налаштування крону на твій графік (6:00, 12:00, 17:00)
    scheduler.add_job(send_morning_message, CronTrigger(hour=6, minute=0))
    scheduler.add_job(send_noon_message, CronTrigger(hour=12, minute=0))
    scheduler.add_job(send_evening_message, CronTrigger(hour=17, minute=0))
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
