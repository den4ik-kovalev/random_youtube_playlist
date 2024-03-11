import asyncio
import random

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import dotenv_values
from loguru import logger

from storage import Storage
from youtube import YouTube


logger.add("error.log", format="{time} {level} {message}", level="ERROR")
token = dotenv_values(".env")["TOKEN"]
bot = Bot(token=token)
dispatcher = Dispatcher()


@dispatcher.message(Command("menu"))
async def cmd_menu(message: types.Message):
    """ Обработчик команды /menu """
    lines = [
        "/config - скачать настройки",
        "/cache - создать файл кэша",
        "/describe - описание режимов",
        "/make - создать плейлист",
        "/fast - создать плейлист из кэша",
        "",
        "Чтобы установить настройки, отправьте config.yml",
        "Чтобы установить кэш, отправьте cache.yml"
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


@dispatcher.message(Command("cache"))
async def cmd_cache(message: types.Message):
    """ Обработчик команды /cache """
    storage = Storage(message.chat.id)
    yt = YouTube(storage)
    yt.create_cache_file()
    file = FSInputFile(storage.cache_file.path)
    await bot.send_document(
        chat_id=message.chat.id,
        document=file
    )


@dispatcher.message(Command("describe"))
async def cmd_describe(message: types.Message):
    """ Обработчик команды /describe """

    storage = Storage(message.chat.id)
    if not storage.mode_2_playlists:
        await message.answer("Нет доступных режимов")
        return

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
        return

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


@dispatcher.message(Command("fast"))
async def cmd_fast(message: types.Message):
    """ Обработчик команды /fast """

    storage = Storage(message.chat.id)
    if not storage.mode_2_playlists:
        await message.answer("Нет доступных режимов")
        return

    builder = InlineKeyboardBuilder()
    for mode in storage.mode_2_playlists:
        builder.add(
            types.InlineKeyboardButton(
                text=mode,
                callback_data=f"fast_{mode}"
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
    elif message.document and message.document.file_name == "cache.yml":
        storage = Storage(message.chat.id)
        await bot.download(
            file=message.document.file_id,
            destination=storage.cache_file.path
        )
        await message.reply("Кэш успешно установлен")


@dispatcher.callback_query(F.data.startswith("describe_"))
async def callbacks_describe(callback: types.CallbackQuery):
    """ Обработчик колбеков кнопок /describe """

    _, mode = callback.data.split("_")

    # Названия плейлистов данного режима
    storage = Storage(callback.message.chat.id)
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
    storage = Storage(callback.message.chat.id)
    urls = storage.mode_2_urls[mode]

    # Список id видео из этих плейлистов
    videos_ids = []
    yt = YouTube(storage)
    for url in urls:
        videos_ids.extend(yt.get_playlist_videos_ids(url))

    if not videos_ids:
        await callback.answer()
        return

    # Выбрать до 50 случайных видео
    size = min([50, len(videos_ids)])
    sample = random.sample(videos_ids, size)

    # Сгенерировать ссылку на плейлист из этих видео
    playlist_link = "http://www.youtube.com/watch_videos?video_ids=" + ",".join(sample)

    await callback.message.answer(playlist_link)
    # Чаще всего не успеваем ответить на колбек
    # aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request:
    # query is too old and response timeout expired or query ID is invalid
    # await callback.answer()


@dispatcher.callback_query(F.data.startswith("fast_"))
async def callbacks_fast(callback: types.CallbackQuery):
    """ Обработчик колбеков кнопок /fast """

    _, mode = callback.data.split("_")

    # Список ссылок на плейлисты данного режима
    storage = Storage(callback.message.chat.id)
    urls = storage.mode_2_urls[mode]

    # Список id видео из этих плейлистов
    videos_ids = []
    yt = YouTube(storage, is_available=False)
    for url in urls:
        videos_ids.extend(yt.get_playlist_videos_ids(url))

    if not videos_ids:
        await callback.answer()
        return

    # Выбрать до 50 случайных видео
    size = min([50, len(videos_ids)])
    sample = random.sample(videos_ids, size)

    # Сгенерировать ссылку на плейлист из этих видео
    playlist_link = "http://www.youtube.com/watch_videos?video_ids=" + ",".join(sample)

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
