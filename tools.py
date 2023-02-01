import logging
import os
import re
import smtplib
from email.mime.image import MIMEImage  # Изображения
from email.mime.multipart import MIMEMultipart
from typing import Union, List

from PIL import Image
from aiogram import Bot
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message, InputFile

from config import TOKEN_API, SIZE, FROM_EMAIL, MY_PASSWORD, HOST, PORT, USERS, FILE_NAME, FORMAT

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

    async def check(self, obj: Message):
        if not obj.document:
            return False

        if obj.document.mime_type in self.mime_types:
            return True

        return False


async def proc_document_or_image(message):
    if message.document:
        if check_tracker(message):
            file_info = await bot.get_file(message.document.file_id)
            await message.document.download(file_info.file_path)
            with Image.open(file_info.file_path) as img:  # Открытие изображения
                await processing_and_saving_image(img)
                # открываем фото для загрузки в телеграм
                photo = InputFile(FILE_NAME)
                # бот может отсылать сообщение как одному пользователю через from_user.id, так и в беседу через chat.id
            await bot.send_photo(chat_id=message.from_user.id, photo=photo,
                                 caption=f'user_id: {message.from_user.id}, datatime: {tconv(message.date)}')
            os.remove(file_info.file_path)
            send_email(FILE_NAME, message.caption)
        else:
            await message.answer(text='Пожалуйста, введите корректный номер задачи')
            await message.delete()
    if message.photo:
        if check_tracker(message):
            file_info = await bot.get_file(message.photo[-1].file_id)
            await message.photo[-1].download(file_info.file_path.split('/')[1])
            with Image.open(file_info.file_path.split('/')[1]) as img:  # Открытие изображения
                await processing_and_saving_image(img)
                # открываем фото для загрузки в телеграм
                photo = InputFile(file_info.file_path.split('/')[1])
                # бот может отсылать сообщение как одному пользователю через from_user.id, так и в беседу через chat.id
            await bot.send_photo(chat_id=message.from_user.id, photo=photo,
                                 caption=f'user.id: {message.from_user.id}, datatime: {tconv(message.date)}')
            os.remove(file_info.file_path.split('/')[1])
            send_email(FILE_NAME, message.caption)
        else:
            await message.answer(text='Пожалуйста, введите корректный номер задачи')
            await message.delete()


async def processing_and_saving_image(img):
    # изменяем размер
    new_image = img.resize(SIZE)
    logging.info(new_image)
    # сохранение картинки
    new_image.save(FILE_NAME)


def send_email(filename, subject):
    file = processing_file(filename)
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


def processing_file(filename):
    with open(filename, 'rb') as fp:
        file = MIMEImage(fp.read())
        file.add_header('Content-Disposition', 'attachment', filename=filename)  # Добавляем заголовки
    return file
