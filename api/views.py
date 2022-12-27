from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.client.crypto_client import CryptoBaseClient
from api.models import MadeRequest
from api.process_message import process_message
from django.utils import timezone

@api_view(["GET"])
def sign_message(request):
    message = request.query_params.get('message')
    content, status_code = process_message(message)

    return Response(content, status=status_code)


@api_view(["GET"])
def verify_message(request):
    message = request.query_params.get('message')
    signature = request.query_params.get('signature')
    client = CryptoBaseClient()
    requests_made_in_the_last_minute = MadeRequest.objects.filter(created__gte=timezone.now()-timedelta(minutes=1)).count()
    if requests_made_in_the_last_minute > 10:
        queue_request(client.verify_message(message, signature))
        return Response(status=202)
    content, status_code = client.verify_message(message, signature)

    return Response(content, status=status_code)


@api_view(["GET"])
def test_api_key(request):
    client = CryptoBaseClient()
    content, status_code = client.test_api_key()
    return Response(content, status=status_code)