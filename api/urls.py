from django.urls import path

from .views import sign_message, verify_message, test_api_key

urlpatterns = [
    path("crypto/sign", sign_message, name="sign_message"),
    path("crypto/verify", verify_message, name="verify_message"),
    path("crypto/test_api_key", test_api_key, name='test_api_key')
]
