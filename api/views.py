from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.client.crypto_client import CryptoBaseClient
from api.models import CryptoMessage
from api.process_message import process_message


@api_view(["GET"])
def sign_message(request):
    message = request.query_params.get("message")
    callback_url = request.query_params.get("callback_url", "")
    if not message:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    crypto_message, _ = CryptoMessage.objects.get_or_create(
        message=message, defaults={"callback_url": callback_url}
    )
    content, status_code = process_message(crypto_message, called_from_view=True)
    return Response(content, status=status_code)


@api_view(["GET"])
def verify_message(request):
    message = request.query_params.get("message")
    signature = request.query_params.get("signature")
    if not message or not signature:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    client = CryptoBaseClient()
    content, status_code = client.verify_message(message, signature)
    return Response(content, status=status_code)


@api_view(["GET"])
def test_api_key(request):
    client = CryptoBaseClient()
    content, status_code = client.test_api_key()
    return Response(content, status=status_code)
