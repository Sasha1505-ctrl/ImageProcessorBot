import logging
import os
import re
import smtplib
from email.mime.image import MIMEImage  # Изображения
from email.mime.multipart import MIMEMultipart
from typing import List, Union

from PIL import Image
from aiogram import types, Bot
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import InputFile
from config import TOKEN_API, SIZE, FROM_EMAIL, MY_PASSWORD, HOST, PORT, USERS, FILE_NAME

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
        caption = message.caption
        pattern = re.compile('^[A-Z]{2}-\d{4}$')
        if caption is not None and re.fullmatch(pattern=pattern, string=caption):
            logging.info(caption)
            await message.document.download(file_info.file_path)
            with Image.open(file_info.file_path) as img:  # Открытие изображения
                # изменяем размер
                new_image = img.resize(SIZE)
                logging.info(new_image)
                # сохранение картинки
                new_image.save(FILE_NAME)
                photo = InputFile(FILE_NAME)
            await bot.send_photo(chat_id=message.from_user.id,
                                 photo=photo, caption=caption)
            os.remove(file_info.file_path)
            send_email(FILE_NAME, caption)
        else:
            await message.answer(text='Пожалуйста, введите номер задачи')
            await message.delete()
    if message.photo:
        file_info = await bot.get_file(message.photo[-1].file_id)
        caption = message.caption
        pattern = re.compile('^[A-Z]{2}-\d{4}$')
        if caption is not None and re.fullmatch(pattern=pattern, string=caption):
            logging.info(caption)
            await message.photo[-1].download(file_info.file_path.split('/')[1])
            with Image.open(file_info.file_path.split('/')[1]) as img:  # Открытие изображения
                # изменяем размер
                new_image = img.resize(SIZE)
                logging.info(new_image)
                # сохранение картинки
                new_image.save(FILE_NAME)
                photo = InputFile(FILE_NAME)
            await bot.send_photo(chat_id=message.from_user.id,
                                 photo=photo, caption=caption)
            os.remove(file_info.file_path.split('/')[1])
            send_email(FILE_NAME, caption)
        else:
            await message.answer(text='Пожалуйста, введите корректный номер задачи')
            await message.delete()


def send_email(filename, subject):
    # Get each user detail and send the email:
    file = processing_file(filename)
    email = USERS
    # set up the SMTP server
    with smtplib.SMTP_SSL(host=HOST, port=PORT) as server:
        server.login(FROM_EMAIL, MY_PASSWORD)
        server.set_debuglevel(True)
        msg = MIMEMultipart()
        # setup the parameters of the message
        msg['Subject'] = subject
        msg.attach(file)  # Присоединяем файл к сообщению
        # send the message via the server set up earlier.
        server.sendmail(FROM_EMAIL, email, msg.as_string())
        del msg


def processing_file(filename):
    with open(filename, 'rb') as fp:
        file = MIMEImage(fp.read())
        file.add_header('Content-Disposition', 'attachment', filename=filename)  # Добавляем заголовки
    return file
