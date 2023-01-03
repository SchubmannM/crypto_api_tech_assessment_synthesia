import logging
from datetime import timedelta

from celery import Celery
from django.utils import timezone

from api.models import CryptoMessage
from api.models import MadeRequest
from api.process_message import process_message

MAX_REQUESTS_PER_MINUTE = 10

app = Celery("crypto_api")

logger = logging.getLogger(__name__)


@app.task
def process_unfulfilled_messages():
    """
    Picks up unfulfilled messages and processes them without any specific order.
    Only x messages are processed, x being a calculated number that depends on how many
    requests were made by the client in the last 60 seconds, as we have a
    10 requests per minutes threshold to honer.
    """
    logger.info("Processing unfulfilled messages")
    requests_made_in_the_last_minute = MadeRequest.objects.filter(
        created__gte=timezone.now() - timedelta(minutes=1)
    ).count()
    logger.info(
        f"{requests_made_in_the_last_minute} requests were made in the last minute"
    )
    allowed_requests = MAX_REQUESTS_PER_MINUTE - requests_made_in_the_last_minute
    logger.info(f"{allowed_requests} new requests can be made")
    if allowed_requests < 1:
        return
    unprocessed_messages = CryptoMessage.objects.filter(
        fulfilled__isnull=True
    ).order_by("-created")
    logger.info(
        f"There are in total {unprocessed_messages.count()} unprocessed messages"
    )
    messages_to_process_not = unprocessed_messages[:allowed_requests]
    logger.info(f"Processing {messages_to_process_not.count()} messages")
    for message in messages_to_process_not:
        reply = process_message(message)
        logger.info(reply)
