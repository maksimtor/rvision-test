from flask import Flask
import clickhouse_connect
import time

import os
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Подключение к кликхаусу.
# Приходится использовать waiting loop из-за того,
# что контейнер с кликхаусом мог еще не загрузиться нормально.
db_ready = False
slept = 0
while not db_ready and slept<6:
    try:
        db_client = clickhouse_connect.get_client(
            host='localhost')
    except Exception as e:
        time.sleep(10)
        slept += 1
        if slept < 6:
            print("Could not connect to clickhouse, retrying.")
        else:
            print("Could not connect to clickhouse.")
            raise e
    else:
        db_ready = True
        print("Connected to clickhouse!")

# Подключение роутов
from anomaly_checker import routes

# Подключение селери
from anomaly_checker import celery_app