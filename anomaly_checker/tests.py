import pytest
import clickhouse_connect
import anomaly_checker.db_funcs
import datetime
import time
from flask import Flask
from anomaly_checker.migrations import initial_migration
from ipaddress import IPv4Address
from anomaly_checker.celery_app import add_anomaly_celery

presets = {
    'vpn_data': [
        ('V_Varkentin', IPv4Address('88.29.25.1'), 37.382282, -5.975701, datetime.datetime.strptime('25.07.2023 16:20:00', '%d.%m.%Y %H:%M:%S').replace(
            tzinfo=datetime.timezone(datetime.timedelta(seconds=21600), '+06')), datetime.datetime.strptime('25.07.2023', '%d.%m.%Y').date()),
        ('I_Ivanov', IPv4Address('88.29.25.1'), 55.15444, 61.42972, datetime.datetime.strptime('27.07.2023 17:00:05', '%d.%m.%Y %H:%M:%S').replace(
            tzinfo=datetime.timezone(datetime.timedelta(seconds=21600), '+06')), datetime.datetime.strptime('27.07.2023', '%d.%m.%Y').date()),
        ('V_Varkentin', IPv4Address('78.29.32.0'), 55.15444, 61.42972, datetime.datetime.strptime('28.07.2023 18:21:17', '%d.%m.%Y %H:%M:%S').replace(
            tzinfo=datetime.timezone(datetime.timedelta(seconds=21600), '+06')), datetime.datetime.strptime('28.07.2023', '%d.%m.%Y').date()),
        ('V_Varkentin', IPv4Address('78.29.32.0'), 37.382282, -5.975701, datetime.datetime.strptime('28.07.2023 20:21:17', '%d.%m.%Y %H:%M:%S').replace(
            tzinfo=datetime.timezone(datetime.timedelta(seconds=21600), '+06')), datetime.datetime.strptime('28.07.2023', '%d.%m.%Y').date()),
    ]
}


def add_preset_vpns():
    for vpn in presets['vpn_data']:
        anomaly_checker.db_funcs.add_vpn(*vpn)


@pytest.fixture(scope='function')
def app():
    app = Flask(__name__)
    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            task_ignore_result=True,
        ),
    )
    yield app


@pytest.fixture(scope='function')
def db():
    db_client = clickhouse_connect.get_client(
        host='localhost')
    return db_client


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_add_vpn(db):
    initial_migration.run_migration()
    vpn_data = ('V_Varkentin', IPv4Address('88.29.25.1'), 37.382282, -5.975701, datetime.datetime.strptime(
        '25.07.2023 16:20:00', '%d.%m.%Y %H:%M:%S'), datetime.datetime.strptime('25.07.2023', '%d.%m.%Y').date())
    anomaly_checker.db_funcs.add_vpn(*vpn_data)
    vpns = db.query("SELECT * from VPN")
    assert vpns.result_rows[0][1:] == vpn_data


def test_add_anomaly(db):
    initial_migration.run_migration()
    anomaly_data = (1, 'V_Varkentin')
    anomaly_checker.db_funcs.add_anomaly(*anomaly_data)
    anomalies = db.query("SELECT * from Anomaly")
    assert anomalies.result_rows[0][1:] == anomaly_data


def test_check_anomalies(db):
    initial_migration.run_migration()
    add_preset_vpns()
    anomaly_checker.db_funcs.check_anomalies()
    anomalies = db.query("SELECT * from Anomaly")
    assert len(anomalies.result_rows) == 1
    assert anomalies.result_rows[0][1:] == (4, 'V_Varkentin')
    anomaly_checker.db_funcs.check_anomalies()
    anomalies = db.query("SELECT * from Anomaly")
    assert len(anomalies.result_rows) == 1


def test_celery_task(db):
    initial_migration.run_migration()
    add_preset_vpns()
    add_anomaly_celery.delay()
    time.sleep(5)
    anomalies = db.query("SELECT * from Anomaly")
    assert len(anomalies.result_rows) == 1
    assert anomalies.result_rows[0][1:] == (4, 'V_Varkentin')
    add_anomaly_celery.delay()
    time.sleep(5)
    anomalies = db.query("SELECT * from Anomaly")
    assert len(anomalies.result_rows) == 1
