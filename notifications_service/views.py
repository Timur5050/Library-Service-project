from datetime import date, timedelta
import requests

from celery import shared_task
from django.conf import settings
from django.db.models import Q

from borrow_service.models import Borrow


def send_message_to_telegram_group(message: str):
    """
    Sends a message to a predefined Telegram group using the Telegram Bot API.
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    message = message

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message
    }
    return requests.post(url, data=payload)


@shared_task
def daily_list_of_borrowers():
    """
    Sends a daily list of borrowers who have to return their books by tomorrow
    via a message to a Telegram group. If there are no pending returns, it informs
    the group that no books are overdue.
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    list_of_borrows = list(Borrow.objects.filter(
        Q(
            expected_return_date__lte=date.today() + timedelta(days=1)
        ) & Q(
            actual_return_date__isnull=True
        )
    ))

    if not list_of_borrows:
        message = "No borrowings overdue today!"
    else:
        message = "list of people that have to return book till tomorrow 23:59:"
        for borrower in list_of_borrows:
            message += f"\n{borrower.user.email}"
        message += "\ngood bye!"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message
    }
    requests.post(url, data=payload)
    return {"message": message}
