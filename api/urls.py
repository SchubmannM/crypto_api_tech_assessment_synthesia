from django.urls import path

from .views import sign_message
from .views import test_api_key
from .views import verify_message

urlpatterns = [
    path("crypto/sign", sign_message, name="sign_message"),
    path("crypto/verify", verify_message, name="verify_message"),
    path("crypto/test_api_key", test_api_key, name="test_api_key"),
]
