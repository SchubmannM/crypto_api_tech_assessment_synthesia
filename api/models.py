from django.db import models


class CryptoMessage(models.Model):
    created = models.DateTimeField(editable=False, auto_now_add=True, null=True)
    message = models.CharField(max_length=2048, unique=True)
    signature = models.CharField(max_length=2048)
    callback_url = models.CharField(max_length=2048)
    fulfilled = models.DateTimeField(null=True)


class MadeRequest(models.Model):
    created = models.DateTimeField(editable=False, auto_now_add=True, null=True)
    url = models.CharField(max_length=2048)
