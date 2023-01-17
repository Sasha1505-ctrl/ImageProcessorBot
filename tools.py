import logging
import os
from typing import List, Union

from PIL import Image
from aiogram import types, Bot
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import InputFile
from config import TOKEN_API, SIZE

bot = Bot(TOKEN_API)

class MimeTypeFilter(BoundFilter):
    """
    Check document mime_type
    """

    key = "mime_type"

    def __init__(self, mime_type: Union[str, List[str]]):
        if isinstance(mime_type, str):
            self.mime_types = [mime_type]

        elif isinstance(mime_type, list):
            self.mime_types = mime_type

        else:
            raise ValueError(
                f"filter mime_types must be a str or list of str, not {type(mime_type).__name__}"
            )

    async def check(self, obj: types.Message):
        if not obj.document:
            return False

        if obj.document.mime_type in self.mime_types:
            return True

        return False


async def proc_document_or_image(message):
    if message.document:
        file_info = await bot.get_file(message.document.file_id)
        await message.document.download(file_info.file_path)
        with Image.open(file_info.file_path) as img:  # Открытие изображения
            # изменяем размер
            new_image = img.resize(SIZE)
            logging.info(new_image)
            # сохранение картинки
            new_image.save('done_image.jpg')
            photo = InputFile('done_image.jpg')
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=photo)
        os.remove(file_info.file_path)
    if message.photo:
        file_info = await bot.get_file(message.photo[-1].file_id)
        await message.photo[-1].download(file_info.file_path.split('/')[1])
        with Image.open(file_info.file_path.split('/')[1]) as img:  # Открытие изображения
            # изменяем размер
            new_image = img.resize(SIZE)
            logging.info(new_image)
            # сохранение картинки
            new_image.save('done_image.jpg')
            photo = InputFile('done_image.jpg')
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=photo)
        os.remove(file_info.file_path.split('/')[1])
