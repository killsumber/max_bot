import unittest
import requests
from unittest.mock import MagicMock, mock_open, patch
from src.utils.bot import MaxBot, BotInfo


class TestMaxBot(unittest.TestCase):

    def setUp(self):
        self.token = "abcd1234efgh5678"
        self.bot = MaxBot(self.token)
        # 🔑 Заменяем реальную сессию на мок — ДО тестов
        self.mock_session = MagicMock()
        self.bot.session = self.mock_session

    def test_init_raises_on_empty_token(self):
        with self.assertRaises(ValueError):
            MaxBot("")

    def test_get_me_success(self):
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "user_id": 987654321,
            "first_name": "TestBot",
            "last_name": None,
            "username": "test_bot",
            "is_bot": True,
            "last_activity_time": 1700000000000,
        }
        mock_response.raise_for_status = MagicMock()
        self.mock_session.request.return_value = mock_response

        # Act
        result = self.bot.get_me()

        # Assert
        self.mock_session.request.assert_called_once_with(
            "GET",
            "https://platform-api.max.ru/me",  # ← без пробелов!
            params={"access_token": self.token},
        )
        self.assertIsInstance(result, BotInfo)
        self.assertEqual(result.user_id, 987654321)

    def test_send_message_with_chat_id(self):
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": {"body": {"mid": "msg123"}}}
        mock_response.raise_for_status = MagicMock()
        self.mock_session.request.return_value = mock_response

        # Act
        result = self.bot.send_message("Hello!", chat_id=1234567890)

        # Assert
        self.mock_session.request.assert_called_once()
        call = self.mock_session.request.call_args
        self.assertEqual(call[0][0], "POST")
        self.assertEqual(call[0][1], "https://platform-api.max.ru/messages")
        self.assertEqual(call[1]["params"]["chat_id"], 1234567890)
        self.assertEqual(call[1]["json"]["text"], "Hello!")
        self.assertEqual(result["message"]["body"]["mid"], "msg123")

    def test_send_message_requires_chat_or_user(self):
        with self.assertRaises(ValueError):
            self.bot.send_message("Hi!")

    @patch("builtins.open", new_callable=mock_open, read_data=b"fake image data")
    def test_get_upload_url_and_upload_file(self, mock_file):
        # Arrange — 2 ответа: upload URL + upload result
        mock_resp_upload = MagicMock()
        mock_resp_upload.json.return_value = {"url": "https://upload.example.com/123"}
        mock_resp_upload.raise_for_status = MagicMock()

        mock_resp_post = MagicMock()
        mock_resp_post.json.return_value = {
            "photos": {"orig": {"token": "photo_xyz789"}}
        }
        mock_resp_post.raise_for_status = MagicMock()

        # Важно: upload_file вызывает self.session.post напрямую!
        # Поэтому нужно мокать и request (для /uploads), и post (для загрузки)
        self.mock_session.request.return_value = mock_resp_upload
        self.mock_session.post.return_value = mock_resp_post

        # Act
        upload_info = self.bot.get_upload_url("image")
        upload_result = self.bot.upload_file(upload_info["url"], "dummy.jpg")

        # Assert
        # 1. get_upload_url вызвал self.session.request("POST", ...)
        self.mock_session.request.assert_called_once_with(
            "POST",
            "https://platform-api.max.ru/uploads",
            params={"access_token": self.token, "type": "image"},
        )

        # 2. upload_file вызвал self.session.post(...)
        self.mock_session.post.assert_called_once_with(
            "https://upload.example.com/123",
            files={"data": mock_file.return_value},
        )

        mock_file.assert_called_once_with("dummy.jpg", "rb")
        self.assertEqual(upload_result["photos"]["orig"]["token"], "photo_xyz789")

    def test_http_error_raises_exception(self):
        # Arrange
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401")
        self.mock_session.request.return_value = mock_response

        # Act & Assert
        with self.assertRaises(requests.exceptions.HTTPError):
            self.bot.get_me()