from datetime import timedelta
from django.utils import timezone
from api.models import CryptoMessage, MadeRequest
from api.process_message import process_message

MAX_REQUESTS_PER_MINUTE = 10

def process_unfulfilled_messages():
    requests_made_in_the_last_minute = MadeRequest.objects.filter(created__gte=timezone.now()-timedelta(minutes=1)).count()
    allowed_requests = MAX_REQUESTS_PER_MINUTE - requests_made_in_the_last_minute
    while allowed_requests > 0:
        unprocessed_messages = CryptoMessage.objects.filter(fulfilled__isnull=True).order_by('created')
        for message in unprocessed_messages:
            process_message(message)
