# Что это такое
Этот телеграм-бот позволяет создавать свои подборки плейлистов на YouTube и делать по-настоящему случайную выборку треков из них

Какие проблемы это решает:
1. Если плейлист достаточно большой, при случайном режиме треки выбираются из первых 200 (в некоторых версиях приложения - около 300-400)
2. Можно разделить один плейлист на несколько (по исполнителям, или по жанрам, или просто чтобы сделать из большого плейлиста несколько мелких),
но не существует режима случайного прослушивания сразу нескольких плейлистов

# Продакшен
На момент написания этой статьи бот доступен по никнейму @random_yt_bot

# Функционал

## Команда /menu
Список доступных команд

## Команда /config
Скачать текущие настройки бота. Если настройки пока не установлены, скачать пример настроек.

## Отправка файла config.yml
Установить настройки бота. В настройках задаются плейлисты (название и URL) и режимы (название и список плейлистов).

## Команда /describe
Список плейлистов в конкретном режиме

## Команда /make
Случайный плейлист (не более 50 треков). Треки выбираются из всех видео всех плейлистов конкретного режима.

# Запуск программы

Инструкция, чтобы запустить программу самостоятельно:
1. Создать нового бота в BotFather
2. `git clone https://github.com/den4ik-kovalev/random_youtube_playlist`
3. Вставить токен бота в .env
4. `python -m venv venv`
5. `source venv/bin/activate`
6. `pip install -r requirements.txt`
7. `python3 main.py`

## pythonanywhere.com
Чтобы задеплоить бота на pythonanywhere.com, необходимо проделать дополнительные шаги (Причина: https://www.pythonanywhere.com/forums/topic/28845/)
7. Переименовать pythonanywhere.py -> main.py
8. `pip install aiohttp-socks`
9. `cd ~/random_youtube_playlist; venv/bin/python3 main.py`

