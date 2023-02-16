import logging
import os
import re
import io
import smtplib
from email.mime.image import MIMEImage  # Изображения
from email.mime.multipart import MIMEMultipart
from typing import Union, List

import requests
from PIL import Image
from aiogram import Bot
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message, InputFile, ChatActions

from config import TOKEN_API, SIZE, FROM_EMAIL, MY_PASSWORD, HOST, PORT, USERS, FORMAT

bot = Bot(TOKEN_API)
URL = f'https://api.telegram.org/bot{TOKEN_API}/getfile?file_id='
URL_GET = f'https://api.telegram.org/file/bot{TOKEN_API}/'


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

    async def check(self, obj: Message):
        if not obj.document:
            return False

        if obj.document.mime_type in self.mime_types:
            return True

        return False


async def proc_document_or_image(message):
    if message.document:
        if check_tracker(message):
            file_info = message.document.file_id
            # бот может отсылать сообщение как одному пользователю через from_user.id, так и в беседу через chat.id
            await ChatActions.upload_photo()
            await message.answer_photo(photo=InputFile(processing_and_saving_image(file_info)),
                                       caption=f'user.id: {message.from_user.id}, datatime: {tconv(message.date)}')
            await send_email(processing_and_saving_image(file_info), message.caption)
        else:
            await message.answer(text='Пожалуйста, введите корректный номер задачи')
            await message.delete()
    if message.photo:
        if check_tracker(message):
            file_info = message.photo[3].file_id
            # бот может отсылать сообщение как одному пользователю через from_user.id, так и в беседу через chat.id
            await ChatActions.upload_photo()
            await message.answer_photo(photo=InputFile(processing_and_saving_image(file_info)),
                                       caption=f'user.id: {message.from_user.id}, datatime: {tconv(message.date)}')
            await send_email(processing_and_saving_image(file_info), message.caption)
        else:
            await message.answer(text='Пожалуйста, введите корректный номер задачи')
            await message.delete()


def processing_and_saving_image(file_info):
    resp = requests.get(URL + file_info)
    img_path = resp.json()['result']['file_path']
    img = requests.get(URL_GET + img_path)
    img = Image.open(io.BytesIO(img.content))
    # изменяем размер
    img = img.resize(SIZE)
    logging.info(img)
    # сохранение картинки
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img.seek(0)
    buffer.seek(0)
    return buffer


async def send_email(buffer, subject):
    file = processing_file(buffer)
    email = USERS
    # настройка SMTP сервера
    with smtplib.SMTP_SSL(host=HOST, port=PORT) as server:
        server.login(FROM_EMAIL, MY_PASSWORD)
        # отчет записывается в консоль
        server.set_debuglevel(True)
        msg = MIMEMultipart()
        # настраиваем параметры письма
        msg['Subject'] = subject
        # Присоединяем файл к сообщению
        msg.attach(file)
        # отправляем сообщение через сервер
        server.sendmail(FROM_EMAIL, email, msg.as_string())
        # делаем письмо пустым для дальнейшей отправки
        del msg


tconv = lambda x: x.strftime("%H:%M:%S %d.%m.%Y")  # Конвертация даты в читабельный вид
check_tracker = lambda message: message.caption is not None and re.fullmatch(pattern=re.compile(FORMAT),
                                                                             string=message.caption)


def processing_file(buffer):
    file = MIMEImage(buffer.read())
    file.add_header('Content-Disposition', 'attachment', filename='processed_image.png')  # Добавляем заголовки
    return file