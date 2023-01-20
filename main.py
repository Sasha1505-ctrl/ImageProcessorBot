import asyncio
from aiogram import Bot, executor, types
from aiogram.dispatcher import Dispatcher
from config import TOKEN_API, SIZE
from tools import MimeTypeFilter, proc_document_or_image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(TOKEN_API)
dp = Dispatcher(bot)

dp.filters_factory.bind(MimeTypeFilter, event_handlers=[dp.message_handlers])

HELP = """
введите команду /start чтобы начать работать с ботом
введите команду /help чтобы узнать команды
введите команду /description чтобы прочитать описание бота
загрузите фото формата .jpg или .png чтобы обработать изображение
"""

DESCRIPTION = f"""
Данный бот принимает изображения и номер задачи, обрабатывает 
изображение до определенного размера {SIZE} и отправляет 
изображение вложением с темой в виде номера задачи на определенную почту
"""


async def on_startup(_):  # sends a notification to console that bot is running
    logging.info("Bot is running")


@dp.message_handler(commands=['start'])  # welcome and launch bot command
async def start_send(message: types.Message):
    await message.answer('Добро пожаловать!')
    await message.delete()


@dp.message_handler(commands=['help'])  # help command
async def help_send(message: types.Message):
    await message.answer(text=HELP)
    await message.delete()


@dp.message_handler(commands=['description'])  # description command
async def description_send(message: types.Message):
    await message.answer(text=DESCRIPTION)
    await message.delete()


@dp.message_handler(
    content_types=types.ContentTypes.DOCUMENT,
    mime_type=["image/jpeg", "image/png"]
)  # image processing command for original photos
async def doc_proc(message: types.Message):
    await proc_document_or_image(message)
    await asyncio.sleep(0.1)


@dp.message_handler(
    content_types=types.ContentTypes.PHOTO
)  # image processing command (for compressed photos)
async def image_proc(message: types.Message):
    await proc_document_or_image(message)
    await asyncio.sleep(0.1)


@dp.message_handler()  # finally command
async def finally_send(message: types.Message):
    await message.answer(text='Пожалуйста, загрузите изображение')
    await message.delete()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
