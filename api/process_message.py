from datetime import timedelta
from typing import Optional, Tuple
from api.client.crypto_client import CryptoBaseClient
from api.models import CryptoMessage, MadeRequest
from django.utils import timezone

from api.tasks import process_crypto_request

def process_message(message: str, callback_url: str = '') -> Tuple[Optional[str], int]:
    crypto_message, _ = CryptoMessage.objects.get_or_create(message=message, defaults={'callback_url': callback_url})
    if crypto_message.signature != '':
        return crypto_message.signature, 200
    client = CryptoBaseClient()
    requests_made_in_the_last_minute = MadeRequest.objects.filter(created__gte=timezone.now()-timedelta(minutes=1)).count()
    if requests_made_in_the_last_minute > 10:
        queue_request('sign', crypto_message.id)
        return None, 202
    content, status_code = client.sign_message(message)
    if status_code == 200:
        return content, status_code
    if status_code == 502:
        queue_request('sign', crypto_message.id)
        return None, 202
    
def queue_request(method, obj_id):
    if method == 'sign':
        process_crypto_request.delay(obj_id)