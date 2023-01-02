import os

from celery import Celery


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crypto_api.settings")

app = Celery("crypto_api")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.broker_url = "redis://redis:6379"
app.conf.result_backend = "redis://redis:6379"
app.conf.task_serializer = "json"
# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    from api.tasks import process_unfulfilled_messages

    sender.add_periodic_task(30.0, process_unfulfilled_messages, expires=10)


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
