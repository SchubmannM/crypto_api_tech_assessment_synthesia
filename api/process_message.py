from datetime import timedelta
from typing import Optional
from typing import Tuple

from django.utils import timezone

from api.client.crypto_client import CryptoBaseClient
from api.models import CryptoMessage
from api.models import MadeRequest


def reply_to_callback(crypto_message: CryptoMessage):
    client = CryptoBaseClient()
    content, status_code = client.send_signature_to_callback_url(crypto_message)
    if status_code == 200:
        if crypto_message.fulfilled is None:
            crypto_message.fulfilled = timezone.now()
            crypto_message.save()
    return content, status_code


def process_message(
    crypto_message: CryptoMessage, *, called_from_view: bool = False
) -> Tuple[Optional[str], int]:
    """
    Processing an instance of CryptoMessage. If this method was called through a view,
    we return the results to the view. Otherwise we call the callback_url with the results.

    If the crypto message already has a signature, we return the signature without calling the api.
    If it was not yet fulfilled (-> the user has not yet received it) then we save the fulfillment time.

    If there is no signature, we contact the API. If we receive a signature, we save it on the object instance
    and return it. Otherwise we return a 202 (if the method was called from a view) or don't do anything
    as all unfulfilled messages will get picked up periodically by the celery worker.
    """
    if crypto_message.signature:
        if called_from_view:
            if crypto_message.fulfilled is None:
                crypto_message.fulfilled = timezone.now()
                crypto_message.save()
            return crypto_message.signature, 200
        else:
            content, status_code = reply_to_callback(crypto_message)
            return content, status_code

    # Signature does not exist in db yet
    client = CryptoBaseClient()
    requests_made_in_the_last_minute = MadeRequest.objects.filter(
        created__gte=timezone.now() - timedelta(minutes=1)
    ).count()
    if requests_made_in_the_last_minute > 9:
        # Too many requests were already made -> Return 202
        return None, 202

    # Try to get signature from API
    content, status_code = client.sign_message(crypto_message.message)
    if status_code == 200:
        crypto_message.signature = content
        crypto_message.save()
        if called_from_view:
            return content, status_code
        else:
            content, status_code = reply_to_callback(crypto_message)
            return content, status_code

    # Could not be retrieved, return 202
    if called_from_view:
        if status_code == 502:
            return None, 202
    return None, 500
    # We can return None for all cases where signature is not yet available.
    # These messages will get picked up by the celery worker (which calls this method)
