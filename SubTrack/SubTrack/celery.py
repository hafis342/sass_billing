import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SubTrack.settings')
app = Celery('SubTrack')

app.config_from_object(settings, namespace='CELERY')


app.conf.beat_schedule = {
    'change-sucsription-status': {
        'task': 'products.tasks.update_subcription_status',
        'schedule': crontab(minute=0, hour=0),
    },
    'generate-invoices-daily': {
        'task': 'products.tasks.generate_subscription_invoices',
        'schedule': crontab(minute=0, hour=0),
    },
}

app.autodiscover_tasks()
