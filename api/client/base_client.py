from datetime import timedelta
import logging
from json import JSONDecodeError
from typing import Literal, Optional
from django.utils import timezone
import requests
from requests.adapters import HTTPAdapter
from requests.auth import AuthBase
from urllib3 import Retry

from api.models import MadeRequest  # type: ignore

logger = logging.getLogger(__name__)


ResponseFormat = Literal["json", "html"]
HTTPMethod = Literal["get", "GET", "post", "POST", "put", "PUT", "delete", "DELETE"]

def build_url(*args):
    """Build a URL from components."""
    return '/'.join(a.strip('/') for a in args)


class BaseAPIClient:
    def __init__(
        self, base_url: str, session_auth: Optional[AuthBase]
    ):
        self._url = base_url
        self._session = requests.Session()

        if session_auth:
            self._session.auth = session_auth

        self._session.mount(
            self._url,
            HTTPAdapter(max_retries=Retry(backoff_factor=0.5, status_forcelist={429})),
        )

    def _send_request(
        self,
        *,
        method: HTTPMethod,
        endpoint: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
    ):
        # allow a full URL to be passed in as endpoint for callback url
        url = (
            endpoint
            if endpoint.lower().startswith("http")
            else build_url(self._url, endpoint)
        )

        args = {
            'method': method.lower(),
            'url': url,
            'timeout': (1,2),
        }

        if params:
            args['params'] = params
        if data:
            args['json'] = data

        response = None
        try:
            MadeRequest.objects.create(url=url)
            response = self._session.request(**args)
            return response

        except JSONDecodeError as e:
            raise e
        except TimeoutError as e:
            raise e

