from flask import Flask
from celery import Celery, Task
from anomaly_checker.db_funcs import check_anomalies
from anomaly_checker import app

# Настройка серели

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

app.config.from_mapping(
    CELERY=dict(
        broker_url="redis://localhost:6379/0",
        result_backend="redis://localhost:6379/0",
        task_ignore_result=True,
    ),
)

celery_app = celery_init_app(app)


# Запускаем раз в 60 секунд проверку логов.
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60, add_anomaly_celery.s(), name='add every 10')

@celery_app.task
def add_anomaly_celery():
    check_anomalies()