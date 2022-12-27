from api.client.base_client import BaseAPIClient

import logging
from typing import Optional

from requests.auth import AuthBase
from requests.models import Request
import os
from dotenv import load_dotenv
logger = logging.getLogger(__name__)

load_dotenv()  # take environment variables from .env.

class CryptoTokenAuth(AuthBase):
    """Attaches HTTP Auth token to requests."""

    def __init__(self):
        self._apikey = os.getenv("API_KEY")

    def __call__(self, request: Request):  # type: ignore
        request.headers["Authorization"] = f"{self._apikey}"
        return request


class CryptoBaseClient(BaseAPIClient):
    def __init__(self, base_url: Optional[str] = None):
        super().__init__(
            base_url=base_url or os.getenv("BASE_URL"),
            session_auth=CryptoTokenAuth(),
        )

    def sign_message(self, message: str):
        response = super()._send_request(
            method="get", endpoint=f"crypto/sign?message={message}"
        )
        return response.content.decode(), response.status_code

    def verify_message(self, message: str, signature: str):
        response = super()._send_request(
            method="get", endpoint=f"crypto/verify?message={message}&signature={signature}"
        )
        return response.content.decode(), response.status_code

    def test_api_key(self):
        response = super()._send_request(method="get", endpoint="")
        return response.content.decode(), response.status_code

    def send_response(self, *, callback_url, signature):
        response = super()._send_request(method="get", endpoint=callback_url, data=signature)
        return response.content.decode(), response.status_code