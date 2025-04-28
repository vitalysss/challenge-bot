import asyncio
from datetime import datetime, date
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ChatType
from aiogram import Router
from tinydb import TinyDB, Query

# === НАСТРОЙКИ ===
# <-- сюда вставь токен своего бота
API_TOKEN = '7173022502:AAFfhEq_iqAvUNE3JTX8HcHB8PgZqhtbkTY'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# === TinyDB для хранения данных ===
db = TinyDB('challenge_data.json')
Challenge = Query()


def save_challenge(chat_id, data):
    db.upsert({**data, 'chat_id': chat_id}, Challenge.chat_id == chat_id)


def load_challenge(chat_id):
    return db.get(Challenge.chat_id == chat_id)


def delete_challenge(chat_id):
    db.remove(Challenge.chat_id == chat_id)


def get_all_challenges():
    return db.all()

# === Хендлеры ===


@router.message(Command('start'))
async def start_handler(message: Message):
    if message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        await message.answer("Привет! Какой сегодня день челленджа? (Напишите просто число)")
    else:
        await message.answer("Этот бот работает только в группах.")


@router.message(Command('status'))
async def status_handler(message: Message):
    chat_id = message.chat.id
    data = load_challenge(chat_id)

    if not data or data.get('waiting_for_total_days'):
        await message.answer("Челлендж ещё не настроен в этой группе.")
        return

    now = datetime.now().date()
    start_date = date.fromisoformat(data['start_date'])
    days_passed = (now - start_date).days
    current_day = data['current_day'] + days_passed
    total_days = data['total_days']
    days_left = (data['current_day'] + total_days) - current_day

    if days_left >= 0:
        await message.answer(f"Сегодня день №{current_day} челленджа!\nОсталось {days_left} дней.")
    else:
        await message.answer("Челлендж уже завершён.")


@router.message(Command('stop'))
async def stop_handler(message: Message):
    chat_id = message.chat.id
    if load_challenge(chat_id):
        delete_challenge(chat_id)
        await message.answer("Напоминания остановлены и данные удалены.")
    else:
        await message.answer("Нет активного челленджа для остановки.")


@router.message()
async def message_handler(message: Message):
    chat_id = message.chat.id
    data = load_challenge(chat_id)

    if not data:
        if message.text.isdigit():
            save_challenge(chat_id, {
                'current_day': int(message.text),
                'waiting_for_total_days': True
            })
            await message.answer("Сколько дней будет длиться челлендж?")
        else:
            await message.answer("Пожалуйста, введите число.")
    elif data.get('waiting_for_total_days'):
        if message.text.isdigit():
            data['total_days'] = int(message.text)
            data['start_date'] = datetime.now().date().isoformat()
            data['waiting_for_total_days'] = False
            save_challenge(chat_id, data)
            await message.answer("Отлично! Буду присылать напоминания каждый день!")
        else:
            await message.answer("Пожалуйста, введите число.")

# === Ежедневная отправка сообщений ===


async def daily_challenge_sender():
    while True:
        now = datetime.now().date()
        for data in get_all_challenges():
            if not data.get('waiting_for_total_days'):
                chat_id = data['chat_id']
                start_date = date.fromisoformat(data['start_date'])
                days_passed = (now - start_date).days
                current_day = data['current_day'] + days_passed
                total_days = data['total_days']

                if current_day <= data['current_day'] + total_days - 1:
                    try:
                        await bot.send_message(chat_id, f"Сегодня день №{current_day} челленджа!")
                    except Exception as e:
                        print(
                            f"Ошибка отправки сообщения в чат {chat_id}: {e}")
                elif current_day == data['current_day'] + total_days:
                    try:
                        await bot.send_message(chat_id, "Поздравляем! Челлендж завершён! 🎉")
                        delete_challenge(chat_id)
                    except Exception as e:
                        print(
                            f"Ошибка отправки сообщения в чат {chat_id}: {e}")
        await asyncio.sleep(86400)  # 24 часа

# === Запуск бота ===


async def main():
    asyncio.create_task(daily_challenge_sender())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
