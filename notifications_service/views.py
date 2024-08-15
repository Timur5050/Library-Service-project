import requests
from django.conf import settings
from django.shortcuts import render


def send_message_to_telegram_group(message: str):
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    message = message

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message
    }
    return requests.post(url, data=payload)
