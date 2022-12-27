from celery import shared_task
from api.client.crypto_client import CryptoBaseClient
from django.utils import timezone
from api.models import CryptoMessage

RATE_LIMIT = 10  # tasks per second
TIME_LIMIT = 60  # seconds
RETRIES_LIMIT = 10  # Maximum number of retries for each task


@shared_task(
    rate_limit=RATE_LIMIT,
    time_limit=TIME_LIMIT,
    max_retries=RETRIES_LIMIT,
    retry_backoff=True,
)
def process_crypto_request(crypto_message_id):
    crypto_client = CryptoBaseClient()
    message = CryptoMessage.objects.get(id=crypto_message_id)
    if message.fulfilled:
        return
    content, status_code = crypto_client.sign_message(message.message)
    if status_code == 200:
        message.signature = content
        message.save()
        response = crypto_client.send_response(callback_url=message.callback_url, signature=message.signature)
        if response.status_code == 200:
            message.fulfilled = timezone.now()
            message.save()

    