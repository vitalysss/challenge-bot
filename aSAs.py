import datetime
import os
import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile  # <-- ВАЖНО! Используем FSInputFile

API_TOKEN = "7072488391:AAFWl4ULMZGNZVTPwqVNIynzMaycLaSYApY"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Даты окончания призывов
END_SPRING = datetime.date(datetime.datetime.now().year, 7, 15)
END_AUTUMN = datetime.date(datetime.datetime.now().year, 12, 31)

# Папка с котиками (укажи абсолютный путь)
# ← убедись, что путь верный
CATS_PHOTOS_DIR = r"C:\Users\dom\OneDrive\Desktop\cats_photos"


def get_days_left():
    today = datetime.date.today()
    if today <= END_SPRING:
        return (END_SPRING - today).days, "весеннего"
    elif today <= END_AUTUMN:
        return (END_AUTUMN - today).days, "осеннего"
    else:
        return (datetime.date(today.year + 1, 7, 15) - today).days, "следующего весеннего"


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    days_left, season = get_days_left()
    text = f"До конца {season} призыва осталось {days_left} дней.\nВот тебе котик 🐱"

    try:
        # Выбираем случайное фото
        cat_photo = random.choice(os.listdir(CATS_PHOTOS_DIR))
        photo_path = os.path.join(CATS_PHOTOS_DIR, cat_photo)

        # Используем FSInputFile для отправки файла
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=text)
    except Exception as e:
        await message.answer(f"{text}\nПроизошла ошибка: {e}")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
