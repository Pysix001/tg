from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
import sqlite3
import logging
import asyncio
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Инициализация
bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# Инициализация БД
def init_db():
    conn = sqlite3.connect('keys.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS keys (key TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS used_keys (key TEXT)''')
    conn.commit()
    conn.close()

# Функции работы с ключами
def load_keys():
    conn = sqlite3.connect('keys.db')
    cursor = conn.cursor()
    cursor.execute("SELECT key FROM keys")
    keys = [row[0] for row in cursor.fetchall()]
    conn.close()
    return keys

def save_keys(keys):
    conn = sqlite3.connect('keys.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM keys")
    cursor.executemany("INSERT INTO keys (key) VALUES (?)", [(k,) for k in keys])
    conn.commit()
    conn.close()

def load_used():
    conn = sqlite3.connect('keys.db')
    cursor = conn.cursor()
    cursor.execute("SELECT key FROM used_keys")
    used = [row[0] for row in cursor.fetchall()]
    conn.close()
    return used

def save_used(used):
    conn = sqlite3.connect('keys.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM used_keys")
    cursor.executemany("INSERT INTO used_keys (key) VALUES (?)", [(k,) for k in used])
    conn.commit()
    conn.close()

# Клавиатуры
start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Ethernaly", callback_data="eth")]
])

period_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1 день", callback_data="sub_1")],
    [InlineKeyboardButton(text="7 дней", callback_data="sub_7")],
    [InlineKeyboardButton(text="30 дней", callback_data="sub_30")]
])

# Обработчики
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Выберите товар:", reply_mup=start_kb)

@dp.callback_query(F.data == "eth")
async def choose_period(call: types.CallbackQuery):
    await call.message.answer("Выберите срок подписки:", reply_markup=period_kb)

@dp.callback_query(F.data.startswith("sub_"))
async def process_sub(call: types.CallbackQuery):
    period = call.data.split("_")[1]
    prices = {'1': '100₽', '7': '500₽', '30': '1000₽'}
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Проверить оплату", callback_data=f"checkpay_{period}")]
    ])
    
    await call.message.answer(
        f"Сумма: {prices.get(period, '100₽')}\nОплатите по ссылке:\nhttps://t.me/your_channel_or_qiwi",
        reply_markup=markup
    )

@dp.callback_query(F.data.startswith("checkpay_"))
async def check_payment(call: types.CallbackQuery):
    keys = load_keys()
    if not keys:
        await call.message.answer("❌ Нет доступных ключей. Напишите в поддержку.")
        return
    
    key = keys.pop(0)
    save_keys(keys)
    
    used = load_used()
    used.append(key)
    save_used(used)
    
    await call.message.answer(f"✅ Оплата подтверждена!\nВаш ключ: `{key}`")

@dp.message(Command("admin"), F.from_user.id == int(os.getenv('ADMIN_ID')))
async def admin_panel(message: types.Message):
    await message.answer("Пришлите ключи в формате:\nKEY1\nKEY2\nKEY3")

@dp.message(F.from_user.id == int(os.getenv('ADMIN_ID')))
async def add_keys(message: types.Message):
    new_keys = [k.strip() for k in message.text.split('\n') if k.strip()]
    keys = load_keys()
    keys.extend(new_keys)
    save_keys(keys)
    await message.answer(f"Добавлено ключей: {len(new_keys)}")

async def main():
    init_db()  # Инициализация БД при старте
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())