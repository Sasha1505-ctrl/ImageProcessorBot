from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN_API, SIZE
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(TOKEN_API)
dp = Dispatcher(bot)

HELP = """
введите команду /start чтобы начать работать с ботом
введите команду /help чтобы узнать команды
введите команду /description чтобы прочитать описание бота
"""

DESCRIPTION = f"""
Данный бот принимает изображения и номер задачи, обрабатывает 
изображение до определенного размера {SIZE} и отправляет 
изображение вложением с темой в виде номера задачи на определенную почту
"""

async def on_startup(_):
    logging.info("Bot is running")

@dp.message_handler(commands=['start'])
async def echo(message: types.Message):
    await message.answer('Добро пожаловать!')
    await message.delete()

@dp.message_handler(commands=['help'])
async def echo(message: types.Message):
    await message.answer(text=HELP)
    await message.delete()

@dp.message_handler(commands=['description'])
async def echo(message: types.Message):
    await message.answer(text=DESCRIPTION)
    await message.delete()

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(text=message.text)
    await message.delete()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)