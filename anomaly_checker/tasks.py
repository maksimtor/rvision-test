from celery import shared_task
from db_funcs import add_anomaly

@shared_task(ignore_result=False)
def add_anomaly_celery():
    add_anomaly(1, 'Hello')