import os

# Telegram Constants
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Yandex Cloud Constants
FOLDER_ID = os.getenv("FOLDER_ID")
SERVICE_ACCOUNT_API_KEY = os.getenv("SERVICE_ACCOUNT_API_KEY")

# API URLs
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Text messages
MESSAGES = {
    "start_help": (
        "Пришлите мне фотографии и я определю и запомню лица людей на них."
    ),
    "unknown_command": "Извините, я не понимаю эту команду. Попробуйте /start или /help.",
    "no_message": "No message to process.",
    "error": "При обработке сообщения произошла ошибка.",
    "incorrect_input": "Я могу обработать только текстовое сообщение или фотографию.\nИспользуйте /help для получения подсказок.",
}