import requests
from typing import (
    Optional,
    List,
    Dict,
    Any,
    Union,
    TypeAlias,
)
from dataclasses import dataclass, asdict
from urllib.parse import urljoin

# ————————————————————————————— Типы —————————————————————————————

# Значение параметра запроса: str, int, bool, list[str], None — всё, что принимает requests
ParamValue: TypeAlias = Union[str, int, bool, List[str], None]
Params: TypeAlias = Dict[str, ParamValue]

# ——————————————————————————— Константы ——————————————————————————

BASE_URL: str = "https://platform-api.max.ru"  # ← без пробелов!

# ——————————————————————————— Dataclasses ——————————————————————————

@dataclass
class BotInfo:
    user_id: int
    first_name: str
    last_name: Optional[str]
    username: Optional[str]
    is_bot: bool
    last_activity_time: int
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    full_avatar_url: Optional[str] = None
    commands: Optional[List[Dict[str, str]]] = None


@dataclass
class NewMessageBody:
    text: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    link: Optional[Dict[str, Any]] = None
    notify: bool = True
    format: Optional[str] = None  # "markdown" or "html"


# ——————————————————————————— Класс MaxBot ——————————————————————————

class MaxBot:
    def __init__(self, token: str):
        if not token or not token.strip():
            raise ValueError("Token must be non-empty")
        self.token = token.strip()
        self.session = requests.Session()

    def _build_url(self, path: str) -> str:
        """Построить полный URL из базы и пути, гарантируя корректную конкатенацию."""
        base = BASE_URL.rstrip("/")
        path = path.lstrip("/")
        return f"{base}/{path}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Params] = None,
        **kwargs,
    ) -> requests.Response:
        """Универсальный метод HTTP-запроса с автоматической подстановкой токена."""
        url = self._build_url(path)
        request_params: Params = dict(params) if params else {}
        request_params["access_token"] = self.token

        resp = self.session.request(method, url, params=request_params, **kwargs)
        resp.raise_for_status()
        return resp

    # ——————————————— Bots ———————————————

    def get_me(self) -> BotInfo:
        """GET /me — информация о боте."""
        resp = self._request("GET", "/me")
        data = resp.json()
        return BotInfo(**data)

    # ——————————————— Messages ———————————————

    def send_message(
        self,
        text: str,
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        format: Optional[str] = None,
        notify: bool = True,
        disable_link_preview: bool = False,
    ) -> dict:
        """POST /messages — отправка сообщения."""
        if not (chat_id or user_id):
            raise ValueError("Either chat_id or user_id must be provided")

        body = NewMessageBody(
            text=text,
            attachments=attachments or [],
            format=format,
            notify=notify
        )

        params: Params = {}
        if user_id is not None:
            params["user_id"] = user_id
        if chat_id is not None:
            params["chat_id"] = chat_id
        if disable_link_preview:
            params["disable_link_preview"] = True  # requests закодирует как "true"

        resp = self._request("POST", "/messages", json=asdict(body), params=params)
        return resp.json()

    def get_updates(
        self,
        limit: int = 100,
        timeout: int = 30,
        marker: Optional[int] = None,
        types: Optional[List[str]] = None,
    ) -> dict:
        """GET /updates — получение обновлений (long polling)."""
        params: Params = {
            "limit": limit,
            "timeout": timeout,
        }
        if marker is not None:
            params["marker"] = marker
        if types:
            # Сервер ожидает строку: "type1,type2"
            params["types"] = ",".join(types)

        resp = self._request("GET", "/updates", params=params)
        return resp.json()

    # ——————————————— Uploads ———————————————

    def get_upload_url(self, file_type: str) -> dict:
        """POST /uploads — получить URL для загрузки файла.
        file_type: 'image', 'video', 'audio', 'file'
        Возвращает: {"url": str, "token"?: str}
        """
        if file_type not in {"image", "video", "audio", "file"}:
            raise ValueError(f"Invalid upload type: {file_type!r}")
        resp = self._request("POST", "/uploads", params={"type": file_type})
        return resp.json()

    def upload_file(self, upload_url: str, file_path: str) -> dict:
        """Загружает файл по URL, полученному через get_upload_url().
        Возвращает JSON с токеном(ами).
        """
        with open(file_path, "rb") as f:
            resp = self.session.post(upload_url, files={"data": f})
            resp.raise_for_status()
            return resp.json()

    def send_photo(self, chat_id: int, file_path: str, caption: str = "") -> dict:
        """Удобный метод: загрузить фото и отправить."""
        info = self.get_upload_url("image")
        upload_url = info["url"]
        upload_result = self.upload_file(upload_url, file_path)

        # Извлекаем токен из результата загрузки фото
        photos = upload_result.get("photos", {})
        if not photos:
            raise ValueError("No photos returned from upload")

        # Берём первый (обычно "orig" или "full")
        first_size_data = next(iter(photos.values()))
        token = first_size_data["token"]

        attachment = {
            "type": "image",
            "payload": {"token": token}
        }

        return self.send_message(caption, chat_id=chat_id, attachments=[attachment])

    def send_video(self, chat_id: int, file_path: str, caption: str = "") -> dict:
        """Удобный метод: загрузить видео и отправить."""
        info = self.get_upload_url("video")
        upload_url = info["url"]
        message_token = info["token"]  # ← токен для вложения в сообщение

        self.upload_file(upload_url, file_path)  # тело игнорируется

        attachment = {
            "type": "video",
            "payload": {"token": message_token}
        }

        return self.send_message(caption, chat_id=chat_id, attachments=[attachment])

    # ——————————————— Chats ———————————————

    def get_chat(self, chat_id: int) -> dict:
        """GET /chats/{chat_id} — информация о чате."""
        resp = self._request("GET", f"/chats/{chat_id}")
        return resp.json()

    def get_chats(self, count: int = 50, marker: Optional[str] = None) -> dict:
        """GET /chats — список чатов."""
        params: Params = {"count": count}
        if marker:
            params["marker"] = marker
        resp = self._request("GET", "/chats", params=params)
        return resp.json()

    # ——————————————— Subscriptions (Webhook) ———————————————

    def subscribe_webhook(
        self,
        url: str,
        update_types: List[str],
        secret: Optional[str] = None,
    ) -> dict:
        """POST /subscriptions — подписка на webhook."""
        body: Dict[str, Any] = {"url": url, "update_types": update_types}
        if secret:
            body["secret"] = secret
        resp = self._request("POST", "/subscriptions", json=body)
        return resp.json()

    def unsubscribe_webhook(self, url: str) -> dict:
        """DELETE /subscriptions — отписка от webhook."""
        resp = self._request("DELETE", "/subscriptions", params={"url": url})
        return resp.json()

    def get_subscriptions(self) -> dict:
        """GET /subscriptions — текущие подписки."""
        resp = self._request("GET", "/subscriptions")
        return resp.json()