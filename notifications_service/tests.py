from django.test import TestCase
from unittest.mock import patch, MagicMock
from datetime import date, timedelta

from django.conf import settings
from borrow_service.models import Borrow
from notifications_service.views import daily_list_of_borrowers


class DailyListOfBorrowersTestCase(TestCase):

    @patch("requests.post")
    def test_no_borrowings_due(self, mock_post):
        with patch("borrow_service.views.Borrow.objects.filter") as mock_filter:
            mock_filter.return_value = []

            result = daily_list_of_borrowers()

            self.assertEqual(result["message"], "No borrowings overdue today!")

            mock_post.assert_called_once_with(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                data={
                    "chat_id": settings.TELEGRAM_CHAT_ID,
                    "text": "No borrowings overdue today!"
                }
            )
