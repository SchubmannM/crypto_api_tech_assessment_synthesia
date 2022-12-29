from datetime import timedelta
from typing import Optional, Tuple
from api.client.crypto_client import CryptoBaseClient
from api.models import CryptoMessage, MadeRequest
from django.utils import timezone

def process_message(crypto_message: CryptoMessage) -> Tuple[Optional[str], int]:
    if crypto_message.signature:
        if crypto_message.fulfilled is None:
            crypto_message.fulfilled = timezone.now()
            crypto_message.save()
        return crypto_message.signature, 200
    client = CryptoBaseClient()
    requests_made_in_the_last_minute = MadeRequest.objects.filter(created__gte=timezone.now()-timedelta(minutes=1)).count()
    if requests_made_in_the_last_minute > 10:
        return None, 202
    content, status_code = client.sign_message(crypto_message.message)
    if status_code == 200:
        crypto_message.signature = content
        crypto_message.fulfilled = timezone.now()
        crypto_message.save()
        return content, status_code
    if status_code == 502:
        return None, 202
    return None, 500
    
       