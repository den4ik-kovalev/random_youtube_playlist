import asyncio
import random

from aiogram import Bot, Dispatcher, types, F
from aiogram.client.session.aiohttp import AiohttpSession  # Added for pythonanywhere
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import dotenv_values
from loguru import logger
from pytube import Playlist

from storage import Storage


logger.add("error.log", format="{time} {level} {message}", level="ERROR")
token = dotenv_values(".env")["TOKEN"]
proxy = "http://proxy.server:3128"  # Added for pythonanywhere
session = AiohttpSession(proxy=proxy)  # Added for pythonanywhere
bot = Bot(token=token, session=session)  # Edited for pythonanywhere
dispatcher = Dispatcher()


@dispatcher.message(Command("menu"))
async def cmd_menu(message: types.Message):
    """ Обработчик команды /menu """
    lines = [
        "/config - скачать настройки",
        "/describe - описание режимов",
        "/make - создать плейлист",
        "",
        "Чтобы установить настройки, отправьте config.yml"
    ]
    await message.answer("\n".join(lines))


@dispatcher.message(Command("config"))
async def cmd_config(message: types.Message):
    """ Обработчик команды /config """
    storage = Storage(message.chat.id)
    if storage.config_file.read():
        file = FSInputFile(storage.config_file.path)
        await bot.send_document(
            chat_id=message.chat.id,
            document=file
        )
    else:
        await bot.send_document(
            chat_id=message.chat.id,
            document=FSInputFile("config_example.yml"),
            caption="Настройки не установлены\nПример файла с настройками"
        )


@dispatcher.message(Command("describe"))
async def cmd_describe(message: types.Message):
    """ Обработчик команды /describe """

    storage = Storage(message.chat.id)
    if not storage.mode_2_playlists:
        await message.answer("Нет доступных режимов")

    builder = InlineKeyboardBuilder()
    for mode in storage.mode_2_playlists:
        builder.add(
            types.InlineKeyboardButton(
                text=mode,
                callback_data=f"describe_{mode}"
            )
        )
    builder.adjust(4)  # 4 кнопки в ряд

    await message.answer("Выберите режим", reply_markup=builder.as_markup())


@dispatcher.message(Command("make"))
async def cmd_make(message: types.Message):
    """ Обработчик команды /make """

    storage = Storage(message.chat.id)
    if not storage.mode_2_playlists:
        await message.answer("Нет доступных режимов")

    builder = InlineKeyboardBuilder()
    for mode in storage.mode_2_playlists:
        builder.add(
            types.InlineKeyboardButton(
                text=mode,
                callback_data=f"make_{mode}"
            )
        )
    builder.adjust(4)  # 4 кнопки в ряд

    await message.answer("Выберите режим", reply_markup=builder.as_markup())


@dispatcher.message()
async def msg_any(message: types.Message):
    """ Обработчик любого другого сообщения """
    if message.document and message.document.file_name == "config.yml":
        storage = Storage(message.chat.id)
        await bot.download(
            file=message.document.file_id,
            destination=storage.config_file.path
        )
        await message.reply("Настройки успешно установлены")


@dispatcher.callback_query(F.data.startswith("describe_"))
async def callbacks_describe(callback: types.CallbackQuery):
    """ Обработчик колбеков кнопок /describe """

    _, mode = callback.data.split("_")

    # Названия плейлистов данного режима
    storage = Storage(callback.chat.id)
    playlists = storage.mode_2_playlists[mode]
    lines = [
        f"<b>{mode}</b>",
        ""
    ]
    lines.extend(playlists)

    await callback.message.answer("\n".join(lines), parse_mode=ParseMode.HTML)
    await callback.answer()


@dispatcher.callback_query(F.data.startswith("make_"))
async def callbacks_make(callback: types.CallbackQuery):
    """ Обработчик колбеков кнопок /make """

    _, mode = callback.data.split("_")

    # Список ссылок на плейлисты данного режима
    storage = Storage(callback.chat.id)
    urls = storage.mode_2_urls[mode]

    # Список видео из этих плейлистов
    videos = []
    for url in urls:
        playlist = Playlist(url)
        videos.extend(list(playlist.videos))

    if not videos:
        await callback.answer()
        return

    # Выбрать до 50 случайных видео
    size = min([50, len(videos)])
    sample = random.sample(videos, size)
    ids = [x.video_id for x in sample]

    # Сгенерировать ссылку на плейлист из этих видео
    playlist_link = "http://www.youtube.com/watch_videos?video_ids=" + ",".join(ids)

    await callback.message.answer(playlist_link)
    # Чаще всего не успеваем ответить на колбек
    # aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request:
    # query is too old and response timeout expired or query ID is invalid
    # await callback.answer()


@logger.catch
async def main():
    """ Ох пойдет щас возня """
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
