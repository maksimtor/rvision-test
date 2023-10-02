# Тестовое задание для R-Vision
Приложение на фласке, использующее селери (на редисе) для выполнения 
главной задачи: проверке логов на аномалии. Бд - кликхаус.
## Запуск
Для запуска приложение необходимы:
1. Docker
2. Docker-compose
3. Docker images: redis:6-alpine, yandex/clickhouse-server

Приложение может быть запущено с помощью этой команды:
```docker-compose up  --build```
## Тестирование
Тесты можно запустить так:
```docker exec -it $container python3 -m pytest -s anomaly_checker/tests.py```

### Ручное тестирование с помощью API:
Так как приложение построено на фласке, я сделал несколько эндпоинтов,
чтобы было легче тестировать его функционал.
- http://127.0.0.1:5000/run_migrations/ - строит таблицы в кликхаусе
- http://127.0.0.1:5000/generate_vpns_fixed/ - генерирует 4 фиксированных лога подключений
- http://127.0.0.1:5000/generate_vpns/<n_vpns> - генерирует n_vpns рандомных лога подключений
- http://127.0.0.1:5000/get_vpns/ - выводит информацию о логах подключений
- http://127.0.0.1:5000/get_anomalies/ - выводит информацию об аномалиях

### Ручное тестирование:
Можно залесть в основной контейнер (web) ```docker exec -it $container bash``` и подключиться к flask shell:
```
export FLASK_APP='run.py'
flask shell
```
#### Внутри фласк шелл:
Там можно создать фиксированные логи подключений:
```
from anomaly_checker.tests import add_preset_vpns
add_preset_vpns()
```
Можно сгенерировать рандомные логи:
```
from anomaly_checker.db_funcs import generate_vpns
generate_vpns(10)
```
Проверить логи и аномалии можно напрямую через подключение к кликхаусу:
```
from anomaly_checker import db_client

vpns = db_client.query("SELECT * FROM VPN")
print(vpns.result_rows)

anomalies = db_client.query("SELECT * FROM Anomaly")
print(anomalies.result_rows)
```