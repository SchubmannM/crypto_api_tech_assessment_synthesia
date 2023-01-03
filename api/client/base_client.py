import logging
from datetime import timedelta
from json import JSONDecodeError
from typing import Literal
from typing import Optional

import requests
from django.db import DatabaseError
from django.utils import timezone
from requests.adapters import HTTPAdapter
from requests.auth import AuthBase

from api.manager import lock_table
from api.models import MadeRequest  # type: ignore

logger = logging.getLogger(__name__)


ResponseFormat = Literal["json", "html"]
HTTPMethod = Literal["get", "GET", "post", "POST", "put", "PUT", "delete", "DELETE"]


def build_url(*args):
    """Build a URL from components."""
    return "/".join(a.strip("/") for a in args)


class BaseAPIClient:
    def __init__(self, base_url: str, session_auth: Optional[AuthBase]):
        self._url = base_url
        self._session = requests.Session()

        if session_auth:
            self._session.auth = session_auth

        self._session.mount(
            self._url,
            HTTPAdapter(max_retries=0),
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
            "method": method.lower(),
            "url": url,
            "timeout": (
                1,
                1,
            ),  # Low timeouts as we MUST return a response within 2 seconds
        }

        if params:
            args["params"] = params
        if data:
            args["json"] = data

        response = requests.Response()
        try:
            try:
                # Lock the table to ensure no new requests are made in between us counting and making a new request
                with lock_table(MadeRequest):
                    if (
                        MadeRequest.objects.filter(
                            created__gte=timezone.now() - timedelta(minutes=1)
                        ).count()
                        < 10
                    ):
                        MadeRequest.objects.create(url=url)
                        response = self._session.request(**args)
                        return response
            except DatabaseError:
                pass
            return response

        except JSONDecodeError as e:
            raise e
        except TimeoutError as e:
            raise e
